from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.booking import Booking
from models.service import Service


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
        ]
    )


def confirm_keyboard(confirm_data: str = "confirm_booking") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=confirm_data,
                ),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
            ],
        ]
    )


def services_keyboard(services: list[Service]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{s.name} — {s.price:.0f} ₽",
            callback_data=f"select_service:{s.id}",
        )]
        for s in services
    ]
    buttons.append(
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def services_catalog_keyboard(services: list[Service]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=s.name,
            callback_data=f"service_info:{s.id}",
        )]
        for s in services
    ]
    buttons.append(
        [InlineKeyboardButton(text="◀️ В меню", callback_data="main_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def my_bookings_keyboard(bookings: list[Booking]) -> InlineKeyboardMarkup:
    buttons = []
    for booking in bookings:
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Отменить #{booking.id}",
                callback_data=f"cancel_booking:{booking.id}",
            ),
            InlineKeyboardButton(
                text=f"🔄 Перенести #{booking.id}",
                callback_data=f"reschedule:{booking.id}",
            ),
        ])
    buttons.append(
        [InlineKeyboardButton(text="◀️ В меню", callback_data="main_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
