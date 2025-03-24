from aiogram.types import \
    ReplyKeyboardMarkup, KeyboardButton

phonenumber_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Nomer yuborish", request_contact=True)
        ]
    ],
    resize_keyboard=True
)
