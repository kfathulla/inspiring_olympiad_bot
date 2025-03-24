import asyncio
import logging
import os
import threading
import socket

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.middlewares.check_subscription import CheckSubscriptionMiddleware
from src.middlewares.config import ConfigMiddleware
from src.config import load_config, Config
from src.handlers import router_list
from src.utils.set_bot_commands import set_default_commands
from src.services import broadcaster
from src.loader import db

# async def on_startup(dispatcher):
#     await set_default_commands(dispatcher)
#
#     await on_startup_notify(dispatcher)

async def on_startup(bot: Bot, admin_ids: list[int]):
    await set_default_commands(bot)
    await broadcaster.broadcast(bot, admin_ids, "Bot ishga tushdi")


def register_global_middlewares(bot: Bot, dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        # DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)

    dp.message.middleware(CheckSubscriptionMiddleware())
    dp.callback_query.middleware(CheckSubscriptionMiddleware())


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


async def main():
    setup_logging()

    try:
        await db.create()
        await db.create_table_users()
    except Exception as ex:
        print(ex)
        
    config = load_config(".env")
    storage = MemoryStorage()
    

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)
    dp.include_routers(*router_list)

    register_global_middlewares(bot, dp, config)
    

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot o'chirildi!")