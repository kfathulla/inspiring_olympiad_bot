from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.filters.callback.tests.test_action import TestActionCallback

test_cancel_submit_keyboard= InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🚫 Bekor qilish", callback_data="test_cancel_submit")
    ]
])

