from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()
    confirm = State()


class RescheduleStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
    confirm = State()
