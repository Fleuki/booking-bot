from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from filters.admin import IsAdmin
from keyboards.admin import admin_bookings_keyboard, admin_menu_keyboard
from services.booking import BookingService
from services.stats import StatsService

router = Router(name="admin")


def _format_bookings_list(title: str, bookings: list) -> str:
    text = f"{title}\n\n"
    text += "\n\n".join(
        f"• {b.format_short()}\n  🆔 user_id: {b.user_id}"
        for b in bookings
    )
    return text


@router.message(Command("admin"), IsAdmin())
async def cmd_admin(message: Message) -> None:
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\nВыберите раздел:",
        reply_markup=admin_menu_keyboard(),
    )


@router.callback_query(F.data == "admin:menu", IsAdmin())
async def admin_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\nВыберите раздел:",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:today", IsAdmin())
async def admin_today(callback: CallbackQuery) -> None:
    service = BookingService()
    bookings = await service.get_today_bookings()

    if not bookings:
        await callback.message.edit_text(
            "📅 На сегодня записей нет.",
            reply_markup=admin_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        _format_bookings_list("📅 <b>Записи на сегодня:</b>", bookings),
        reply_markup=admin_bookings_keyboard(bookings, view="today"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:week", IsAdmin())
async def admin_week(callback: CallbackQuery) -> None:
    service = BookingService()
    bookings = await service.get_week_bookings()

    if not bookings:
        await callback.message.edit_text(
            "📆 На ближайшую неделю записей нет.",
            reply_markup=admin_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        _format_bookings_list("📆 <b>Записи на неделю вперёд:</b>", bookings),
        reply_markup=admin_bookings_keyboard(bookings, view="week"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats", IsAdmin())
async def admin_stats(callback: CallbackQuery) -> None:
    stats = await StatsService().get_monthly_stats()
    popular = stats.popular_service or "—"

    await callback.message.edit_text(
        "📊 <b>Статистика за текущий месяц</b>\n\n"
        f"📋 Всего записей: {stats.total_bookings}\n"
        f"⭐ Самая популярная услуга: {popular}\n"
        f"👥 Уникальных клиентов: {stats.unique_clients}",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_cancel:"), IsAdmin())
async def admin_cancel_booking(callback: CallbackQuery) -> None:
    _, view, booking_id_str = callback.data.split(":", 2)
    booking_id = int(booking_id_str)
    service = BookingService()

    cancelled = await service.cancel_booking(booking_id)
    if not cancelled:
        await callback.answer("Запись не найдена или уже отменена", show_alert=True)
        return

    await callback.answer(f"Запись #{booking_id} отменена")

    if view == "today":
        bookings = await service.get_today_bookings()
        title = "📅 <b>Записи на сегодня:</b>"
    else:
        bookings = await service.get_week_bookings()
        title = "📆 <b>Записи на неделю вперёд:</b>"

    if not bookings:
        await callback.message.edit_text(
            f"✅ Запись #{booking_id} отменена.\n\nЗаписей больше нет.",
            reply_markup=admin_menu_keyboard(),
        )
        return

    await callback.message.edit_text(
        f"✅ Запись #{booking_id} отменена.\n\n"
        + _format_bookings_list(title, bookings),
        reply_markup=admin_bookings_keyboard(bookings, view=view),
    )
