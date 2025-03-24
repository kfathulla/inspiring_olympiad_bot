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


register_router = Router()

@register_router.message(PrivateFilter(), Command("register"))
async def register_command(message: Message, state: FSMContext, bot: Bot):
    try:     
        user = await db.select_user(telegram_id=message.chat.id)
        if user.is_registered:
            await message.answer(text="👋 Botga hush kelibsiz!\nQuyidagi o'zingizga kerakli tugmani bosing", reply_markup=menu_keyboards)
        else:
            await state.set_state(RegistrFormState.Fullname)
            await message.answer(text="Iltimos to'liq ismingizni kiriting.", reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.error(ex)

@register_router.message(PrivateFilter(), RegistrFormState.Fullname)
async def register_fullname_handler(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(fullname=message.text)
        await state.set_state(RegistrFormState.Phone)
        text = ("Iltimos \"Nomerni yuborish\" tugmasini bosing.")
        await message.answer(text=text, reply_markup=phonenumber_keyboard)
    except Exception as ex:
        logging.error(ex)


@register_router.message(PrivateFilter(), RegistrFormState.Phone)
async def register_phone_form(message: Message, state: FSMContext):
    try:
        data = await state.update_data(phone=message.contact.phone_number.strip('+'))
        await db.update_user(data["fullname"], message.from_user.username, data["phone"], True, message.chat.id)
        await state.clear()
        await message.answer(text="Siz muvaffaqiyatli ro'yhatdan o'tdingiz.\nQuyidagi o'zingizga kerakli tugmani bosing", reply_markup=menu_keyboards)
    except Exception as ex:
        logging.error(ex)
    
