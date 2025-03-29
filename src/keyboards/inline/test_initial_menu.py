from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.filters.callback.tests.test_action import TestActionCallback

def test_initial_menu(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️ Testni boshqarish", callback_data=TestActionCallback(test_id=test_id, action="manage").pack()),
        ],
        [
            InlineKeyboardButton(text="➕ Ochiq(kalitsiz) test qo'shish", callback_data=TestActionCallback(test_id=test_id, action="tests/add_open_answers").pack())
        ]
    ])