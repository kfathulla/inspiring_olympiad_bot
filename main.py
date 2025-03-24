from aiogram import executor

from src.loader import dp
import src.middlewares, src.filters, src.handlers
from src.utils.set_bot_commands import set_default_commands
from src.utils.notify_admins import on_startup_notify


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
