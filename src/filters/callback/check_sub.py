from aiogram.filters.callback_data import CallbackData

class CheckSubCallback(CallbackData, prefix="check_subs"):
    referrer_id: int | None = None