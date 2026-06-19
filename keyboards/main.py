from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.service import Service


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться", callback_data="book")],
            [InlineKeyboardButton(text="📋 Мои записи", callback_data="my_bookings")],
            [InlineKeyboardButton(text="💇 Каталог услуг", callback_data="services")],
        ]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ В меню", callback_data="main_menu")],
        ]
    )
