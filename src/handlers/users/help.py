from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router, F, Bot
from src.filters.private_chat_filter import PrivateFilter


help_router = Router()

@help_router.message(PrivateFilter(), Command("help"))
async def bot_help(message: Message):
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
