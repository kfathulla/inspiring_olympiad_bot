from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def mini_course_menu_keyboards(private_channel_link):
    inline_keyboards = [
        [
            InlineKeyboardButton(text="🔗 Taklif posti 🔗", callback_data="courses/intensive_course/referral_post"),
        ],
        [
            InlineKeyboardButton(text="📊 Ballarim 📊", callback_data="courses/intensive_course/referral_ball"),
        ]
    ]
    
    if private_channel_link:
        inline_keyboards.append([
            InlineKeyboardButton(text="📢 Kanalga qo'shilish", url=private_channel_link)
        ])
        
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboards)