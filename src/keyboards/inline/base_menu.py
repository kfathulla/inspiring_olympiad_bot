from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_base_menu_keyboards(private_channel_link):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Bonus kanalga o'tish", url=private_channel_link
                )
            ],
            [
                InlineKeyboardButton(text="➕ Test joylash", callback_data="tests/add"),
            ],
            [
                InlineKeyboardButton(text="📜 Testlarim", callback_data="testlarim"),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Testga javob berish", callback_data="tests/submit"
                )
            ],
        ]
    )


def base_menu_keyboards(private_channel_link):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Bonus kanalga o'tish", url=private_channel_link
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Testga javob berish", callback_data="tests/submit"
                )
            ],
            [
                InlineKeyboardButton(text="📜 Testlarim", callback_data="testlarim"),
            ],
        ]
    )
