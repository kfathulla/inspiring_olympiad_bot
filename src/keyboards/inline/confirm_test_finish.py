from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.filters.callback.tests.test_action import TestActionCallback

def confirm_test_finish(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=TestActionCallback(test_id=test_id, action="confirm_finish").pack()),
        ],
        [
            InlineKeyboardButton(text="🚫 Yo'q", callback_data=TestActionCallback(test_id=test_id, action="cancel_finish").pack())
        ]
    ])