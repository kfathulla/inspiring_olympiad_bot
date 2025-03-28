from datetime import time
import logging

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command

from src.database.repo.requests import RequestsRepo
from src.filters.admins_filter import AdminFilter
from src.filters.private_chat_filter import PrivateFilter
from src.states.send_ad import SendAdState
from src.utils.broadcaster import broadcast


admin_ad_router = Router()

@admin_ad_router.message(PrivateFilter(), AdminFilter(), Command("ad"))
async def send_ad(message: Message, state: FSMContext):
    try:
        await state.set_state(SendAdState.Message)
        await message.answer(text="Iltimos reklama xabarini yuboring.", reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.error("")
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_ad_router.message(PrivateFilter(), SendAdState.Message)
async def send_ad_handler(message: Message, bot: Bot, state: FSMContext, repo: RequestsRepo):
    try:
        users = await repo.users.get_all()
        user_ids = [user.telegram_id for user in users]
        for i in range(1000):
            user_ids.append(user_ids[0])
            user_ids.append(user_ids[1])
            
        count = await broadcast(bot, user_ids, "", message.chat.id, message.message_id, False)
        
        await state.clear()
        await message.answer(text=f"Reklama muvaffaqiyatli yuborildi. \nJami: {count} ta", reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")