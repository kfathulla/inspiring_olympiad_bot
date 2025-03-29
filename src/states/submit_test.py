from aiogram.fsm.state import StatesGroup, State


class SubmitTestState(StatesGroup):
    Answer = State()
