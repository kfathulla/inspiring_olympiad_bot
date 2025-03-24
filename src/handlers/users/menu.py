from aiogram import types

from src.filters import PrivateFilter
from src.loader import dp


@dp.message_handler(PrivateFilter(), state=None)
async def test(message: types.Message):
    try:
        await message.answer(text="test")
    except Exception as ex:
        print(ex)
