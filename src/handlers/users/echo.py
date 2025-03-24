from aiogram import types

from src.filters import PrivateFilter
from src.loader import dp


@dp.message_handler(PrivateFilter())
async def bot_echo(message: types.Message):
    await message.answer("something went wrong. Please try again."
                         "\nIf it doesn't help, contact the admins")
