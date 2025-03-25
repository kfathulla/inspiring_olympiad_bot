import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command

from src.config import Config
from src.database.repo.requests import RequestsRepo
from src.filters.private_chat_filter import PrivateFilter
from src.keyboards.default.cancel import cancel_button
from src.keyboards.default.phonenumber_keyboard import phonenumber_keyboard
from src.keyboards.default.menu_keyboards import menu_keyboards 
from src.states.registr_form import RegistrFormState


register_router = Router()

@register_router.message(PrivateFilter(), Command("register"))
async def register_command(message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:     
        user = await repo.users.get_by_id(message.from_user.id)
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
async def register_phone_form(message: Message, state: FSMContext, repo: RequestsRepo):
    try:
        data = await state.update_data(phone=message.contact.phone_number.strip('+'))
        await repo.users.update_user(message.from_user.id, data["fullname"], data["phone"], True)
        await state.clear()
        await message.answer(text="Tabriklaymiz siz muvaffaqiyatli Ramazon Olimpiadasiga ro'yhatdan o'tdingiz.\nQuyidagi o'zingizga kerakli tugmani bosing", reply_markup=menu_keyboards)
    except Exception as ex:
        logging.error(ex)
    
