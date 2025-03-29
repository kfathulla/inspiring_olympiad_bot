from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.models.tests import Test
from src.filters.callback.tests.test_action import TestActionCallback

def test_list(tests: List[Test]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for test in tests:
        builder.button(
            text=f"{'⛔️' if test.is_finished else '⌛️'}{test.id} - {test.name.title()}",
            callback_data=TestActionCallback(test_id=test.id, action="manage"),
        )
        
    return builder.adjust(3, repeat=True).as_markup()
    