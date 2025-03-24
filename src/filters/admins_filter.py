from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.config import Config


class AdminFilter(BaseFilter):
    async def __call__(self, message: Union[Message, CallbackQuery], config: Config) -> bool:
        # Get the chat and user ID depending on the event type
        if isinstance(message, Message):
            user_id = message.from_user.id
        elif isinstance(message, CallbackQuery):
            user_id = message.from_user.id
        else:
            return False

        # Check the user's status in the chat
        try:
            return user_id in config.tg_bot.admin_ids
        except Exception as e:
            print(f"Error checking admin status: {e}")
            return False
