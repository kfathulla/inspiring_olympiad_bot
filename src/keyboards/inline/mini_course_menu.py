from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

mini_course_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🔗 Taklif posti 🔗", callback_data="courses/mini_course/referral_post"),
    ],
    [
        InlineKeyboardButton(text="📊 Ballarim 📊", callback_data="courses/mini_course/referral_ball"),
    ]
])