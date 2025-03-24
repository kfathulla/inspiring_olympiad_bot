from aiogram.fsm.state import StatesGroup, State


class RegistrFormState(StatesGroup):
    Fullname = State()
    Phone = State()
