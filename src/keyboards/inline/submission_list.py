from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.models.submissions import Submission
from src.filters.callback.tests.test_action import TestActionCallback

def submission_list(submissions: List[Submission]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for submission in submissions:
        builder.button(
            text=f"{'⛔️' if False else '⌛️'}{submission.test.id} - {submission.test.name.title()}",
            callback_data=TestActionCallback(test_id=submission.test.id, action="my_result"),
        )
        
    return builder.adjust(3, repeat=True).as_markup()
    