from aiogram import types, Bot


async def set_default_commands(bot: Bot):
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Botni ishga tushurish"),
            types.BotCommand(command="testlarim", description="Mening testlarim")
        ]
    )
