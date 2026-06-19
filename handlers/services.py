from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.booking import services_catalog_keyboard
from keyboards.main import back_to_menu_keyboard, main_menu_keyboard
from services.service_catalog import ServiceCatalog

router = Router(name="services")


@router.callback_query(F.data == "services")
async def show_services_catalog(callback: CallbackQuery) -> None:
    catalog = ServiceCatalog()
    services = await catalog.get_all()

    text = "💇 <b>Каталог услуг</b>\n\nВыберите услугу для подробностей:"
    await callback.message.edit_text(
        text,
        reply_markup=services_catalog_keyboard(services),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("service_info:"))
async def show_service_info(callback: CallbackQuery) -> None:
    service_id = int(callback.data.split(":")[1])
    catalog = ServiceCatalog()
    service = await catalog.get_by_id(service_id)

    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await callback.message.edit_text(
        service.format_card(),
        reply_markup=services_catalog_keyboard(await catalog.get_all()),
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "👋 Главное меню\n\nВыберите действие:",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()
