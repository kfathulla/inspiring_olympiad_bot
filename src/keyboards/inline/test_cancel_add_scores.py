from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.filters.callback.tests.test_action import TestActionCallback

def test_cancel_add_scores(test_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 Bekor qilish", callback_data=TestActionCallback(test_id=test_id, action="cancel_add_scores").pack())
        ]
    ])

