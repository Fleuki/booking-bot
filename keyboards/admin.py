from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.booking import Booking


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📅 Записи на сегодня",
                callback_data="admin:today",
            )],
            [InlineKeyboardButton(
                text="📆 Записи на неделю",
                callback_data="admin:week",
            )],
            [InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin:stats",
            )],
        ]
    )


def admin_bookings_keyboard(
    bookings: list[Booking],
    view: str,
) -> InlineKeyboardMarkup:
    buttons = []
    for booking in bookings:
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Отменить #{booking.id} — {booking.client_name}",
                callback_data=f"admin_cancel:{view}:{booking.id}",
            ),
        ])
    buttons.append(
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
