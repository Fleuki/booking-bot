from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main import main_menu_keyboard

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Добро пожаловать в сервис записи!\n\n"
        "Выберите действие:",
        reply_markup=main_menu_keyboard(),
    )
