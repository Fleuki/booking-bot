from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.booking import cancel_keyboard, confirm_keyboard, my_bookings_keyboard
from keyboards.main import back_to_menu_keyboard, main_menu_keyboard
from services.booking import BookingService
from states.booking import RescheduleStates
from utils.datetime_utils import format_date_display, format_date_storage, parse_date, parse_time

router = Router(name="my_bookings")


@router.callback_query(F.data == "my_bookings")
async def show_my_bookings(callback: CallbackQuery) -> None:
    service = BookingService()
    bookings = await service.get_user_future_bookings(callback.from_user.id)

    if not bookings:
        await callback.message.edit_text(
            "У вас нет предстоящих записей.",
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    text = "📋 <b>Ваши предстоящие записи:</b>\n\n"
    text += "\n\n".join(f"• {b.format_short()}" for b in bookings)

    await callback.message.edit_text(
        text,
        reply_markup=my_bookings_keyboard(bookings),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_booking:"))
async def cancel_user_booking(callback: CallbackQuery) -> None:
    booking_id = int(callback.data.split(":")[1])
    service = BookingService()
    booking = await service.get_by_id(booking_id)

    if not booking or booking.user_id != callback.from_user.id:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    cancelled = await service.cancel_booking(booking_id)
    if cancelled:
        await callback.answer("Запись отменена")
    else:
        await callback.answer("Не удалось отменить запись", show_alert=True)
        return

    bookings = await service.get_user_future_bookings(callback.from_user.id)
    if not bookings:
        await callback.message.edit_text(
            "✅ Запись отменена.\n\nУ вас больше нет предстоящих записей.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    text = "✅ Запись отменена.\n\n📋 <b>Ваши предстоящие записи:</b>\n\n"
    text += "\n\n".join(f"• {b.format_short()}" for b in bookings)
    await callback.message.edit_text(
        text,
        reply_markup=my_bookings_keyboard(bookings),
    )


@router.callback_query(F.data.startswith("reschedule:"))
async def start_reschedule(callback: CallbackQuery, state: FSMContext) -> None:
    booking_id = int(callback.data.split(":")[1])
    service = BookingService()
    booking = await service.get_by_id(booking_id)

    if not booking or booking.user_id != callback.from_user.id:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    await state.update_data(reschedule_booking_id=booking_id)
    await state.set_state(RescheduleStates.waiting_for_date)
    await callback.message.edit_text(
        f"Перенос записи #{booking_id}\n\n"
        f"Текущая дата: {format_date_display(booking.booking_date)} "
        f"в {booking.booking_time}\n\n"
        "Введите новую дату (ДД.ММ.ГГГГ):",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(RescheduleStates.waiting_for_date, F.text)
async def reschedule_date(message: Message, state: FSMContext) -> None:
    parsed = parse_date(message.text)
    if not parsed:
        await message.answer(
            "Неверный формат даты. Используйте ДД.ММ.ГГГГ",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(booking_date=format_date_storage(parsed))
    await state.set_state(RescheduleStates.waiting_for_time)
    await message.answer(
        "Введите новое время (ЧЧ:ММ):",
        reply_markup=cancel_keyboard(),
    )


@router.message(RescheduleStates.waiting_for_time, F.text)
async def reschedule_time(message: Message, state: FSMContext) -> None:
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
        "Подтвердите перенос записи:\n\n"
        f"📅 {format_date_display(data['booking_date'])} в {time_str}",
        reply_markup=confirm_keyboard(confirm_data="confirm_reschedule"),
    )
    await state.set_state(RescheduleStates.confirm)


@router.callback_query(RescheduleStates.confirm, F.data == "confirm_reschedule")
async def confirm_reschedule(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    booking_id = data["reschedule_booking_id"]
    service = BookingService()
    booking = await service.get_by_id(booking_id)

    if not booking or booking.user_id != callback.from_user.id:
        await state.clear()
        await callback.answer("Запись не найдена", show_alert=True)
        return

    success = await service.reschedule_booking(
        booking_id,
        data["booking_date"],
        data["booking_time"],
    )
    await state.clear()

    if success:
        await callback.message.edit_text(
            f"✅ Запись #{booking_id} перенесена!\n\n"
            f"📅 {format_date_display(data['booking_date'])} "
            f"в {data['booking_time']}",
            reply_markup=back_to_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            "Не удалось перенести запись.",
            reply_markup=back_to_menu_keyboard(),
        )
    await callback.answer()
