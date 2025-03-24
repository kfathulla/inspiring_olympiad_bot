import uuid

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from src.config.config import CHANNELS, ADMINS
from src.filters import PrivateFilter
from src.keyboards.default.menu_keyboards import menu_keyboards
from src.loader import dp, bot, services
from src.models.users import User, UserFilter
from src.utils.misc import subscription


@dp.message_handler(PrivateFilter(), CommandStart(), state=None)
async def start(message: types.Message):
    try:
        user = User()
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
        user.username = message.from_user.username or uuid.uuid4().__str__()
        user.telegram_id = message.from_user.id

        user = await services.user_service.add_or_update_user(user)

        users = await services.user_service.get_all_users(user_filter=UserFilter(updated_datetime_from=None,
                                                                                 updated_datetime_to=None))

        await message.answer(text="Pastdan oʻzingizga kerakli boʻlimni tanlang", reply_markup=menu_keyboards)

        msg = f"{user.__dict__} bazaga qo'shildi.\nBazada {users.total_count} ta foydalanuvchi bor."
        for admin in ADMINS:
            await bot.send_message(chat_id=admin, text=msg)
    except Exception as ex:
        print(ex)


@dp.callback_query_handler(text="check_subs")
async def check_subs(call: types.CallbackQuery):
    await call.answer()
    result = str()
    for channel in CHANNELS:
        status = await subscription.check(user_id=call.from_user.id, channel=channel)
        channel = await bot.get_chat(channel)
        if status:
            result += f"✔ <b>{channel.title}</b> kanaliga obuna bo'lgansiz! \n\n"
        else:
            invite_link = await channel.export_invite_link()
            result += (f"❌️<b>{channel.title}</b> kanaliga obuna bo'lmagansiz. "
                       f"<a href='{invite_link}'>Obuna bo'ling</a> \n\n")

    await call.message.answer(result, disable_web_page_preview=True)
