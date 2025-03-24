from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from src.filters.private_chat_filter import PrivateFilter

echo_router = Router()


@echo_router.message(PrivateFilter(), F.text, StateFilter(None))
async def bot_echo(message: types.Message):
    text = ["Echo.", "Xabar:", message.text]

    await message.answer("\n".join(text))


@echo_router.message(PrivateFilter(), F.text)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f"Echo {hcode(state_name)}",
        "Xabar mazmuni:",
        hcode(message.text),
    ]
    await message.answer("\n".join(text))
