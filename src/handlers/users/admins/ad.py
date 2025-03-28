import asyncio
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
        progress_message = await message.answer("🔃 Reklama jo'natish boshlandi...")
        total_count = 0
        offset, limit = 0, 100
        while True:
            users = await repo.users.get_all(offset=offset, limit=limit)
            if not users:
                break
            
            user_ids = [user.telegram_id for user in users]
            count = await broadcast(bot, user_ids, "", message.chat.id, message.message_id, False)
            total_count+=count
            await progress_message.edit_text(
                f"⏳ Jo'natilmoqda... {total_count-count}+{count}={total_count} ta foydalanuvchiga yetkazildi"
            )

            offset += limit
            await asyncio.sleep(1)
            
        
        await state.clear()
        await message.answer(text=f"Reklama muvaffaqiyatli yuborildi. \nJami: {total_count} ta", reply_markup=ReplyKeyboardRemove())
        await progress_message.delete()
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")