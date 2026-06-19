from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.booking import cancel_keyboard, confirm_keyboard, services_keyboard
from keyboards.main import back_to_menu_keyboard
from services.booking import BookingService
from services.service_catalog import ServiceCatalog
from states.booking import BookingStates
from utils.datetime_utils import format_date_display, format_date_storage, parse_date, parse_time

router = Router(name="booking")


@router.callback_query(F.data == "book")
async def start_booking(callback: CallbackQuery, state: FSMContext) -> None:
    catalog = ServiceCatalog()
    services = await catalog.get_all()
    await state.set_state(BookingStates.waiting_for_service)
    await callback.message.edit_text(
        "Выберите услугу:",
        reply_markup=services_keyboard(services),
    )
    await callback.answer()


@router.callback_query(
    BookingStates.waiting_for_service,
    F.data.startswith("select_service:"),
)
async def select_service(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = int(callback.data.split(":")[1])
    catalog = ServiceCatalog()
    service = await catalog.get_by_id(service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await state.update_data(service_id=service_id, service_name=service.name)
    await state.set_state(BookingStates.waiting_for_name)
    await callback.message.edit_text(
        f"Вы выбрали: <b>{service.name}</b>\n\nВведите ваше имя:",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(BookingStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(client_name=message.text.strip())
    await state.set_state(BookingStates.waiting_for_date)
    await message.answer(
        "Введите желаемую дату (например: 25.06.2026):",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.waiting_for_date, F.text)
async def process_date(message: Message, state: FSMContext) -> None:
    parsed = parse_date(message.text)
    if not parsed:
        await message.answer(
            "Неверный формат даты. Используйте ДД.ММ.ГГГГ",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(booking_date=format_date_storage(parsed))
    await state.set_state(BookingStates.waiting_for_time)
    await message.answer(
        "Введите желаемое время (например: 14:30):",
        reply_markup=cancel_keyboard(),
    )


@router.message(BookingStates.waiting_for_time, F.text)
async def process_time(message: Message, state: FSMContext) -> None:
    parsed = parse_time(message.text)
    if not parsed:
        await message.answer(
            "Неверный формат времени. Используйте ЧЧ:ММ",
            reply_markup=cancel_keyboard(),
        )
        return

    time_str = parsed.strftime("%H:%M")
    data = await state.get_data()
    await state.update_data(booking_time=time_str)

    await message.answer(
        "Проверьте данные записи:\n\n"
        f"💇 Услуга: {data['service_name']}\n"
        f"👤 Имя: {data['client_name']}\n"
        f"📅 Дата: {format_date_display(data['booking_date'])}\n"
        f"🕐 Время: {time_str}\n\n"
        "Подтвердить запись?",
        reply_markup=confirm_keyboard(),
    )
    await state.set_state(BookingStates.confirm)


@router.callback_query(BookingStates.confirm, F.data == "confirm_booking")
async def confirm_booking(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    service = BookingService()

    booking_id = await service.create_booking(
        user_id=callback.from_user.id,
        client_name=data["client_name"],
        service_id=data["service_id"],
        booking_date=data["booking_date"],
        booking_time=data["booking_time"],
    )

    await state.clear()
    await callback.message.edit_text(
        f"✅ Запись #{booking_id} успешно создана!\n\n"
        f"💇 {data['service_name']}\n"
        f"📅 {format_date_display(data['booking_date'])} "
        f"в {data['booking_time']}",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено.",
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()
