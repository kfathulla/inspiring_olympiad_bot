import logging
import uuid

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from src.config import Config
from src.database.repo.requests import RequestsRepo
from src.filters.private_chat_filter import PrivateFilter
from src.filters.admins_filter import AdminFilter
from src.keyboards.inline.base_menu import admin_base_menu_keyboards
from src.utils.misc import subscription 
from src.states.registr_form import RegistrFormState
from src.database.models.users import User

admin_start_router = Router()

@admin_start_router.message(PrivateFilter(), AdminFilter(), CommandStart())
async def user_start(message: Message, state: FSMContext, user: User, bot: Bot, repo: RequestsRepo, command_args: str):
    try:     
        if user is None:                
            user = await repo.users.get_or_create_user(
                message.from_user.id,
                f"{message.from_user.first_name} {message.from_user.last_name}", 
                message.chat.id,
                message.from_user.username or uuid.uuid4().__str__())

        if user.is_registered == True:
            await message.answer(text="👋 Botga hush kelibsiz!\nQuyidagilardan birini tanlang! 👇", reply_markup=admin_base_menu_keyboards(user.private_channel_link))
        else:
            referrer_id = int(command_args) if command_args and command_args and command_args.isdigit() else None
            await state.set_state(RegistrFormState.Fullname)
            await state.update_data(referrer_id=referrer_id)
            await message.answer(text="Iltimos to'liq ismingizni kiriting.", reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.error(ex)