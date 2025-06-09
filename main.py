from contextlib import asynccontextmanager
import logging
from typing import List

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import Update
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.database.setup import create_session_pool, create_engine
from src.middlewares.check_subscription import CheckSubscriptionMiddleware
from src.middlewares.database import DatabaseMiddleware
from src.middlewares.command_parse import CommandParseMiddleware
from src.middlewares.config import ConfigMiddleware
from src.config import load_config, Config
from src.handlers import router_list
from src.utils import broadcaster
from src.utils.set_bot_commands import set_default_commands

# Setup logging first
def setup_logging():
    """
    Set up logging configuration for the application.
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=log_level,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")

setup_logging()

# Initialize config
config = load_config(".env")

# Global bot and dispatcher instances
bot: Bot = None
dp: Dispatcher = None

def get_storage(config: Config):
    logging.info(f"user_redis: {config.tg_bot.use_redis}")
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()

async def on_startup(bot: Bot, admin_ids: List[int], webhook_url: str):
    """
    Perform startup operations including setting webhook and default commands.
    """
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != webhook_url:
            await bot.set_webhook(
                url=webhook_url
            )
        await set_default_commands(bot)
        await broadcaster.broadcast(bot, admin_ids, text="Bot ishga tushdi")
        logging.info("Bot started successfully")
    except Exception as e:
        logging.error(f"Startup error: {e}")
        raise

def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    """
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool)
    ]

    dp.message.middleware(CommandParseMiddleware())
    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)

    dp.message.middleware(CheckSubscriptionMiddleware())
    dp.callback_query.middleware(CheckSubscriptionMiddleware())

async def initialize_bot():
    """
    Initialize bot and dispatcher with all necessary components.
    """
    global bot, dp
    
    storage = get_storage(config=config)
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    dp.include_routers(*router_list)

    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)
    register_global_middlewares(dp, config, session_pool)

async def startup_event():
    """
    FastAPI startup event handler.
    """
    try:
        await initialize_bot()
        webhook_url = f"{config.tg_bot.webhook_url}/webhook"
        await on_startup(bot, config.tg_bot.admin_ids, webhook_url)
    except Exception as e:
        logging.critical(f"Failed to start bot: {e}")
        raise

async def shutdown_event():
    """
    FastAPI shutdown event handler.
    """
    try:
        if bot:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.session.close()
            logging.info("Closed bot session successfully")
    except Exception as e:
        logging.error(f"Shutdown error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    await shutdown_event()

app = FastAPI(title="Telegram Bot Webhook", lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle Telegram webhook updates with proper error handling.
    """
    print(bot)
    if not bot or not dp:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bot not initialized"
        )

    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot=bot, update=update)
        return JSONResponse(content={"ok": True})
    except Exception as e:
        logging.error(f"Webhook processing error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"ok": False, "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    try:
        # app.add_event_handler("startup", startup_event)
        # app.add_event_handler("shutdown", shutdown_event)
        uvicorn.run(
            "main:app",
            host=config.tg_bot.webhook_server_host,
            port=config.tg_bot.webhook_server_port,
            reload=False,
            log_level="info"
        )
    except (KeyboardInterrupt, SystemExit) as e:
        logging.info(f"Bot stopped gracefully {e}")
    except Exception as e:
        logging.critical(f"Fatal error: {e}")