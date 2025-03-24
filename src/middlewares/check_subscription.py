from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from typing import Callable, Awaitable, Dict, Any

from aiogram.types import TelegramObject, User, Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.keyboards.inline.subscription import check_button
from src.config import Config
from src.utils.misc import subscription


class CheckSubscriptionMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        if isinstance(event, Message) and event.chat.type != ChatType.PRIVATE:
            return await handler(event, data)  # Skip middleware in non-private chats

        if isinstance(event, CallbackQuery) and event.message.chat.type != ChatType.PRIVATE:
            return await handler(event, data)

        event_user: User = data['event_from_user']
        bot: Bot = data['bot']
        config: Config = data['config']

        if isinstance(event, Message):
            if event.text in ['/help']:
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            if event.data == "check_subs":
                return await handler(event, data)
        else:
            return await handler(event, data)

        msg = """Assalomu alaykum. Tabriklaymiz siz Umumiy jamg'armasi 20.000.000 so'm bo'lgan Ramazon olimpiadasiga qatnashish imkoniyatiga ega bo'ldingiz.

Olimpiadaga to'liq ro'yhatdan o'tish uchun quyidagi kanallarga a'zo bo'ling."""
        is_subscribed = True
        check_button = InlineKeyboardMarkup(
            inline_keyboard=[[]]
        )
        for channel in config.misc.channel_ids:
            status = await subscription.check(bot=bot, user_id=event_user.id, channel=channel)
            is_subscribed *= status
            channel = await bot.get_chat(channel)
            if not status:
                invite_link = await channel.export_invite_link()
                check_button.inline_keyboard.append([InlineKeyboardButton(url=invite_link, text=channel.title)])

        if not is_subscribed:
            check_button.inline_keyboard.append([InlineKeyboardButton(text="✅ A'zo bo'ldim", callback_data="check_subs")])
            if isinstance(event, Message):
                await event.answer(msg, disable_web_page_preview=True, reply_markup=check_button)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(msg, disable_web_page_preview=True, reply_markup=check_button)
            return

        return await handler(event, data)
