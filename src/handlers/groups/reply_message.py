import logging
import re

from aiogram import Router, F, Bot
from aiogram.types import Message

from src.filters.group_filter import GroupFilter

reply_message_router = Router()


@reply_message_router.message(GroupFilter(), F.reply_to_message)
async def reply_message_handler(message: Message, bot: Bot):
    original_message = message.reply_to_message
    match = re.search(r'Yangi xabar: (-?\d+)\s+user_id: (-?\d+)', original_message.text)
    if match:
        message_id = match.group(1)
        user_id = match.group(2)
        await message.send_copy(chat_id=user_id, reply_to_message_id=message_id)