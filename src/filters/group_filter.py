from typing import Union

from aiogram.enums.chat_type import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class GroupFilter(BaseFilter):
    async def __call__(self, message: Union[Message, CallbackQuery]) -> bool:
        chat_type = message.chat.type if isinstance(message, Message) else message.message.chat.type
        return chat_type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP
        )
