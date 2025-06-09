from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, User
from aiogram.filters.command import CommandObject
from datetime import datetime, timezone, timedelta

from src.database.repo.requests import RequestsRepo
from src.config import Config


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            repo = RequestsRepo(session)
            bot: Bot = data['bot']
            config: Config = data['config']
            command: CommandObject = data.get("command")
            referral_id = int(command.args) if command and command.args and command.args.isdigit() else None
            referral_id = referral_id if referral_id != event.from_user.id else None
            user = await repo.users.get_by_id(event.from_user.id)
            if user is None:
                referrer = await repo.users.get_by_id(referral_id) if referral_id else None
                if referrer:
                    await repo.users.update_user(referrer.user_id, referrer.full_name, referrer.phone, referrer.is_registered, referral_count=referrer.referral_count+1)
                    try:
                        await bot.send_message(
                            referrer.user_id,
                            text=f"🎉 Sizning havolangiz orqali yangi foydalanuvchi ro'yxatdan o'tdi.\nJami taklif qilinganlar soni: {referrer.referral_count}ta.",
                        )
                    except Exception as e:
                        pass
                event_user: User = data['event_from_user']             
                user = await repo.users.get_or_create_user(
                    event.from_user.id,
                    f"{event.from_user.first_name} {event.from_user.last_name}", 
                    event_user.id,
                    event.from_user.username,
                    referrer.user_id if referrer else None
                )

            if user.private_channel_link is None:
                channel = await bot.get_chat(config.misc.private_channel)
                expire_at = int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())
                invite_link = await channel.create_invite_link(expire_date=expire_at, member_limit=1)
                await repo.users.update_user(user.user_id, user.full_name, user.phone, user.is_registered, private_channel_link=invite_link.invite_link, referral_count=user.referral_count)

            data["session"] = session
            data["repo"] = repo
            data["user"] = user

            result = await handler(event, data)
        return result