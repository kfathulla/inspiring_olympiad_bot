from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from src.filters import PrivateFilter
from src.loader import dp


@dp.message_handler(PrivateFilter(), CommandHelp())
async def bot_help(message: types.Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam")

    await message.answer("\n".join(text))

#
# @dp.message_handler(PrivateFilter(), CommandSettings())
# async def bot_help(message: types.Message):
#     text = "Sozlamalar"
#
#     await message.answer(text)
