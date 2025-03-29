from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_base_menu_keyboards = InlineKeyboardMarkup(
    inline_keyboard=[
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

base_menu_keyboards = InlineKeyboardMarkup(
    inline_keyboard=[
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
