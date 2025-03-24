import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command

from src.config import Config
from src.filters.private_chat_filter import PrivateFilter
from src.keyboards.default.cancel import cancel_button
from src.keyboards.default.phonenumber_keyboard import phonenumber_keyboard
from src.keyboards.default.menu_keyboards import menu_keyboards 
from src.states.registr_form import RegistrFormState
from src.loader import db


profile_router = Router()

@profile_router.message(PrivateFilter(), Command("profile"))
async def profile_command(message: Message, state: FSMContext, bot: Bot):
    try:     
        user = await db.select_user(telegram_id=message.chat.id)
        if user.is_registered:
            await message.answer(text=f"Sizning profilingiz:\nIsm: {user.fullname}\nTelefon raqam: {user.phone}")
            await message.answer(text="👋 Botga hush kelibsiz!\nQuyidagi o'zingizga kerakli tugmani bosing", reply_markup=menu_keyboards)
        else:
            await state.set_state(RegistrFormState.Fullname)
            await message.answer(text="Iltimos to'liq ismingizni kiriting.", reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.error(ex)

@profile_router.message(PrivateFilter(), F.text == "👤 Profil")
async def profile(message: Message, state: FSMContext, bot: Bot):
    try:     
        user = await db.select_user(telegram_id=message.chat.id)
        if user['is_registered'] == True:
            await message.answer(text=f"Sizning profilingiz:\nIsm: {user['fullname']}\nTelefon raqam: {user['phone']}")
            await message.answer(text="Quyidagi o'zingizga kerakli tugmani bosing", reply_markup=menu_keyboards)
        else:
            await state.set_state(RegistrFormState.Fullname)
            await message.answer(text="Iltimos to'liq ismingizni kiriting.", reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.error(ex)