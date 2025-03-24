from typing import Union

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest


async def check(bot: Bot, user_id, channel: Union[int, str]) -> bool:
    try:
        member = await bot.get_chat_member(user_id=user_id, chat_id=channel)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except TelegramBadRequest:
        return False

