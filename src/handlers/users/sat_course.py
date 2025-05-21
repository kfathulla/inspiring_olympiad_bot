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


sat_course_router = Router()


@sat_course_router.callback_query(PrivateFilter(), F.data == "sat_course/info")
async def sat_course_info(callback: CallbackQuery, user: User, config: Config):
    try:
        await callback.message.answer(
            text="SAT kursi haqida ma'lumotlar:\n\n"
            "1.  May olimpiadasi \n\n"
            "2. SAT MATH MARAFON 10 \n\n"
            "3. 20 Millionlik Grantlar olimpiadasi \n\n"
            "4. Qo'shimcha ma'lumotlar: Kurs davomida sizga barcha kerakli materiallar taqdim etiladi."
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@sat_course_router.callback_query(PrivateFilter(), F.data == "sat_course/send_homework")
async def sat_course_send_homework(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(SendHomeworkState.Homework)
        await callback.message.answer(text="Iltimos, vazifangizni yuboring.")
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@sat_course_router.message(PrivateFilter(), SendHomeworkState.Homework)
async def send_homework(
    message: Message, state: FSMContext, bot: Bot, config: Config, user: User
):
    try:
        await message.answer(
            text="Vazifangiz qabul qilindi.",
            reply_markup=(
                admin_base_menu_keyboards(user.private_channel_link)
                if message.from_user.id in config.tg_bot.admin_ids
                else base_menu_keyboards(user.private_channel_link)
            ),
        )
        await state.clear()
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")
