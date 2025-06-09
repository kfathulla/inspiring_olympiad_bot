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
from src.database.models.users import User
from src.keyboards.inline.base_menu import (
    base_menu_keyboards,
    admin_base_menu_keyboards,
)

register_router = Router()


@register_router.message(PrivateFilter(), Command("register"))
async def register_command(
    message: Message, state: FSMContext, config: Config, bot: Bot, repo: RequestsRepo
):
    try:
        user = await repo.users.get_by_id(message.from_user.id)
        if user.is_registered:
            await message.answer(
                text="👋 Botga hush kelibsiz!\nQuyidagi o'zingizga kerakli tugmani bosing",
                reply_markup=(
                    admin_base_menu_keyboards(user.private_channel_link)
                    if message.from_user.id in config.tg_bot.admin_ids
                    else base_menu_keyboards(user.private_channel_link)
                ),
            )
        else:
            await state.set_state(RegistrFormState.Fullname)
            await message.answer(
                text="Iltimos to'liq ismingizni kiriting.",
                reply_markup=ReplyKeyboardRemove(),
            )
    except Exception as ex:
        logging.error(ex)


@register_router.message(PrivateFilter(), RegistrFormState.Fullname)
async def register_fullname_handler(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(fullname=message.text)
        await state.set_state(RegistrFormState.Phone)
        text = 'Iltimos "Nomerni yuborish" tugmasini bosing.'
        await message.answer(text=text, reply_markup=phonenumber_keyboard)
    except Exception as ex:
        logging.error(ex)


@register_router.message(PrivateFilter(), RegistrFormState.Phone)
async def register_phone_form(
    message: Message, state: FSMContext, user: User, repo: RequestsRepo, config: Config, bot: Bot
):
    try:
        data = await state.update_data(phone=message.contact.phone_number.strip("+"))
        await repo.users.update_user(
            id=message.from_user.id,
            full_name=data["fullname"],
            phone=data["phone"],
            is_registered=True,
            private_channel_link=user.private_channel_link,
            referral_count=user.referral_count
        )
        await state.clear()
        await message.answer(text="Tabriklaymiz siz muvaffaqiyatli ro'yhatdan o'tdingiz.", reply_markup=ReplyKeyboardRemove())
        await message.answer(
            text="Quyidagi o'zingizga kerakli tugmani bosing",
            reply_markup=(
                admin_base_menu_keyboards(user.private_channel_link)
                if message.from_user.id in config.tg_bot.admin_ids
                else base_menu_keyboards(user.private_channel_link)
            ),
        )
        referrer_id = data['referrer_id']
        referrer = await repo.users.get_by_id(referrer_id) if referrer_id else None
        if referrer:
            try:
                await repo.users.update_user(
                    id=message.from_user.id,
                    full_name=data["fullname"],
                    phone=data["phone"],
                    is_registered=True,
                    private_channel_link=user.private_channel_link,
                    referral_count=user.referral_count,
                    referrer_id=referrer_id
                )
                await repo.users.update_user(
                    referrer.user_id,
                    referrer.full_name,
                    referrer.phone,
                    referrer.is_registered,
                    private_channel_link=user.private_channel_link,
                    referral_count=referrer.referral_count+1
                )
                await bot.send_message(
                    referrer.user_id,
                    text=f"🎉 Sizning havolangiz orqali yangi foydalanuvchi ro'yxatdan o'tdi.\nJami taklif qilinganlar soni: {referrer.referral_count}ta.",
                )
            except Exception as e:
                pass
    except Exception as ex:
        logging.error(ex)
