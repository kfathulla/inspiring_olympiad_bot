import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from src.config import Config
from src.database.repo.requests import RequestsRepo
from src.filters.private_chat_filter import PrivateFilter
from src.states.send_homework import SendHomeworkState
from src.keyboards.inline.base_menu import (
    base_menu_keyboards,
    admin_base_menu_keyboards,
)
from src.database.models.users import User


olympiad_router = Router()


@olympiad_router.callback_query(PrivateFilter(), F.data == "olympiad/may")
async def sat_course_info(callback: CallbackQuery, user: User, config: Config):
    try:
        await callback.message.answer(
            text="May olimpiadasi haqida ma'lumot tez orada joylanadi."
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@olympiad_router.callback_query(PrivateFilter(), F.data == "olympiad/grands")
async def sat_course_send_homework(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.answer(
            text="Grandlar olimpiadasi haqida ma'lumot tez orada joylanadi."
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )
