from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.filters.callback.tests.test_action import TestActionCallback

def test_cancel_adding_open_answers_menu(test_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Ortga", callback_data=TestActionCallback(test_id=test_id, action="cancel_adding_open_answers").pack())
        ]
    ])

