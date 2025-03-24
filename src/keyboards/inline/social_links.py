from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

social_link_keyboards = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Youtube", url="https://www.youtube.com/@"),
    ],
    [
        InlineKeyboardButton(text="Telegram", url="https://t.me/")
    ],
    [
        InlineKeyboardButton(text="Instagram", url="https://www.instagram.com/")
    ],
])
