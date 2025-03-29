from aiogram.filters.callback_data import CallbackData

class TestActionCallback(CallbackData, prefix="test_action"):
    test_id: int
    action: str