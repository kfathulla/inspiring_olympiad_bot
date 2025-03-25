from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, User

from src.database.repo.requests import RequestsRepo


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

            user = await repo.users.get_by_id(event.from_user.id)
            if user is None:   
                event_user: User = data['event_from_user']             
                user = await repo.users.get_or_create_user(
                    event.from_user.id,
                    f"{event.from_user.first_name} {event.from_user.last_name}", 
                    event_user.id,
                    event.from_user.username)

            data["session"] = session
            data["repo"] = repo
            data["user"] = user

            result = await handler(event, data)
        return result