from aiogram.fsm.state import StatesGroup, State


class SendAdState(StatesGroup):
    Message = State()
