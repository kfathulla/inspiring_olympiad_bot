from aiogram import types, Router, Bot, F

from src.filters.group_filter import GroupFilter
from src.filters.admins_filter import AdminFilter

cleaner_router = Router()


@cleaner_router.message(GroupFilter(), F.new_chat_member)
async def new_member(message: types.Message):
    await message.delete()
    # members = ", ".join([m.get_mention(as_html=True) for m in message.new_chat_members])
    # await message.reply(f"Xush kelibsiz, {members}.")


@cleaner_router.message (GroupFilter(), F.left_chat_member)
async def left_member(message: types.Message, bot: Bot):
    await message.delete()
    # if message.left_chat_member.id == message.from_user.id:
    #     await message.answer(f"{message.left_chat_member.get_mention(as_html=True)} guruhni tark etdi")
    # elif message.from_user.id == bot.id:
    #     return
    # else:
    #     await message.answer(f"{message.left_chat_member.fullname} guruhdan haydaldi"
    #                          f"\nadmin: {message.from_user.get_mention(as_html=True)}.")