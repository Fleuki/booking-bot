from datetime import datetime, timedelta

from aiogram import Bot

from models.booking import Booking
from models.database import get_connection
from utils.datetime_utils import (
    booking_datetime,
    format_date_display,
    today_storage,
    week_ahead_storage,
)


class BookingService:
    _BOOKING_SELECT = """
        SELECT b.*, s.name AS service_name
        FROM bookings b
        JOIN services s ON s.id = b.service_id
    """

    async def create_booking(
        self,
        user_id: int,
        client_name: str,
        service_id: int,
        booking_date: str,
        booking_time: str,
    ) -> int:
        db = await get_connection()
        cursor = await db.execute(
            """
            INSERT INTO bookings (
                user_id, client_name, service_id, booking_date, booking_time
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, client_name, service_id, booking_date, booking_time),
        )
        await db.commit()
        return cursor.lastrowid

    async def get_by_id(self, booking_id: int) -> Booking | None:
        db = await get_connection()
        cursor = await db.execute(
            f"{self._BOOKING_SELECT} WHERE b.id = ?",
            (booking_id,),
        )
        row = await cursor.fetchone()
        return Booking.from_row(row) if row else None

    async def get_user_future_bookings(self, user_id: int) -> list[Booking]:
        db = await get_connection()
        cursor = await db.execute(
            f"""
            {self._BOOKING_SELECT}
            WHERE b.user_id = ? AND b.status = 'active'
            ORDER BY b.booking_date, b.booking_time
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        bookings = [Booking.from_row(row) for row in rows]
        return [
            b for b in bookings
            if self._is_future(b.booking_date, b.booking_time)
        ]

    async def get_today_bookings(self) -> list[Booking]:
        today = today_storage()
        db = await get_connection()
        cursor = await db.execute(
            f"""
            {self._BOOKING_SELECT}
            WHERE b.status = 'active' AND b.booking_date = ?
            ORDER BY b.booking_time
            """,
            (today,),
        )
        rows = await cursor.fetchall()
        return [Booking.from_row(row) for row in rows]

    async def get_week_bookings(self) -> list[Booking]:
        today = today_storage()
        week_end = week_ahead_storage()
        db = await get_connection()
        cursor = await db.execute(
            f"""
            {self._BOOKING_SELECT}
            WHERE b.status = 'active'
              AND b.booking_date >= ?
              AND b.booking_date <= ?
            ORDER BY b.booking_date, b.booking_time
            """,
            (today, week_end),
        )
        rows = await cursor.fetchall()
        return [Booking.from_row(row) for row in rows]

    async def cancel_booking(self, booking_id: int) -> bool:
        db = await get_connection()
        cursor = await db.execute(
            """
            UPDATE bookings SET status = 'cancelled'
            WHERE id = ? AND status = 'active'
            """,
            (booking_id,),
        )
        await db.commit()
        return cursor.rowcount > 0

    async def reschedule_booking(
        self,
        booking_id: int,
        booking_date: str,
        booking_time: str,
    ) -> bool:
        db = await get_connection()
        cursor = await db.execute(
            """
            UPDATE bookings
            SET booking_date = ?, booking_time = ?, reminder_sent = 0
            WHERE id = ? AND status = 'active'
            """,
            (booking_date, booking_time, booking_id),
        )
        await db.commit()
        return cursor.rowcount > 0

    async def get_pending_reminders(self) -> list[Booking]:
        db = await get_connection()
        cursor = await db.execute(
            f"""
            {self._BOOKING_SELECT}
            WHERE b.status = 'active' AND b.reminder_sent = 0
            """,
        )
        rows = await cursor.fetchall()
        now = datetime.now()
        window_start = now + timedelta(minutes=52)
        window_end = now + timedelta(minutes=68)

        result: list[Booking] = []
        for row in rows:
            booking = Booking.from_row(row)
            dt = booking_datetime(booking.booking_date, booking.booking_time)
            if dt and window_start <= dt <= window_end:
                result.append(booking)
        return result

    async def mark_reminder_sent(self, booking_id: int) -> None:
        db = await get_connection()
        await db.execute(
            "UPDATE bookings SET reminder_sent = 1 WHERE id = ?",
            (booking_id,),
        )
        await db.commit()

    @staticmethod
    def _is_future(date_str: str, time_str: str) -> bool:
        dt = booking_datetime(date_str, time_str)
        return dt is not None and dt > datetime.now()


async def send_booking_reminders(bot: Bot) -> None:
    service = BookingService()
    reminders = await service.get_pending_reminders()

    for booking in reminders:
        try:
            await bot.send_message(
                booking.user_id,
                "⏰ Напоминание: через 1 час у вас запись!\n\n"
                f"{booking.format_short()}",
            )
            await service.mark_reminder_sent(booking.id)
        except Exception:
            continue
