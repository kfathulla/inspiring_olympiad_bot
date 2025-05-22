import asyncio
from datetime import time, datetime
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
        await message.answer(
            text="Iltimos reklama xabarini yuboring.",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as ex:
        logging.error("")
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")


@admin_ad_router.message(PrivateFilter(), SendAdState.Message)
async def send_ad_handler(
    message: Message, bot: Bot, state: FSMContext, repo: RequestsRepo
):
    try:
        asyncio.create_task(send_ad(bot, repo, message.chat.id, ad_message=message))
        await message.answer(
            text="Reklama xabari backgroundda yuborilmoqda.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")


async def send_ad(bot: Bot, repo: RequestsRepo, admin_id: int, ad_message: Message):
    progress_message = await bot.send_message(
        admin_id, text="🔃 Reklama jo'natish boshlandi...\n"
    )
    start_time = datetime.now()
    total_count = 0
    i, offset, limit = 0, 0, 100
    while True:
        i += 1
        users = await repo.users.get_all(offset=offset, limit=limit)
        if not users:
            break

        user_ids = [user.telegram_id for user in users]
        count = await broadcast(
            bot, user_ids, "", admin_id, ad_message.message_id, False
        )
        total_count += count
        await progress_message.edit_text(
            f"⏳ Jo'natilmoqda... \n{i}. {total_count-count}+{count}={total_count} ta foydalanuvchiga yetkazildi"
        )

        offset += limit
        await asyncio.sleep(1)

    duration = datetime.now() - start_time
    await progress_message.delete()
    await bot.send_message(
        admin_id,
        text=f"Reklama muvaffaqiyatli yuborildi. \nJami: {total_count} ta.\nVaqt: {duration.__str__()}.\n\n",
        reply_markup=ReplyKeyboardRemove(),
    )
