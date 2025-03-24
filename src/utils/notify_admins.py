import logging

from aiogram import Dispatcher

from src.config import Config


async def on_startup_notify(dp: Dispatcher):
    for admin in Config.tg_bot.admin_ids:
        try:
            await dp.bot.send_message(admin, "Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)
