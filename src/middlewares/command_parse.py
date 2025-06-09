from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

class CommandParseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.text and event.text.startswith('/'):
            parts = event.text.split(maxsplit=1)
            command_name = parts[0][1:]
            command_args = parts[1] if len(parts) > 1 else ""

            data["command_name"] = command_name
            data["command_args"] = command_args

        return await handler(event, data)
