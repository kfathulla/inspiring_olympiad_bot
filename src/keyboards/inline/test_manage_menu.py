from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.filters.callback.tests.test_action import TestActionCallback

def test_manage_menu(test_id: int, is_show_correct_count: bool, is_show_incorrects: bool, is_show_answers: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{'✅' if is_show_correct_count else '❌'} Nechta topganini berilishi", callback_data=TestActionCallback(test_id=test_id, action="switch_show_correct_count").pack())
        ],
        [
            InlineKeyboardButton(text=f"{'✅' if is_show_incorrects else '❌'} Qaysi xatoligini berilishi", callback_data=TestActionCallback(test_id=test_id, action="switch_show_incorrects").pack())
        ],
        [
            InlineKeyboardButton(text=f"{'✅' if is_show_answers else '❌'} To'g'ri javoblar berilishi", callback_data=TestActionCallback(test_id=test_id, action="switch_show_answers").pack())
        ],
        [
            InlineKeyboardButton(text="🧮 Ball qo'shish", callback_data=TestActionCallback(test_id=test_id, action="add_scores").pack())
        ],
        [
            InlineKeyboardButton(text="📊 Test ma'lumoti", callback_data=TestActionCallback(test_id=test_id, action="info").pack()),
            InlineKeyboardButton(text="🏁 Testni yakunlash", callback_data=TestActionCallback(test_id=test_id, action="finish").pack())
        ]
    ])
    