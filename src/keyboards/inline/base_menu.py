from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_base_menu_keyboards(private_channel_link):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚 SAT Math marafon 10", callback_data="sat_course/info"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Mini kurs",
                    callback_data="courses/intensive_course",
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text="🗂 Vazifaga javob berish",
            #         callback_data="sat_course/send_homework",
            #     )
            # ],
            [
                InlineKeyboardButton(text="➕ Test joylash", callback_data="tests/add"),
            ],
            [
                InlineKeyboardButton(text="📜 Testlarim", callback_data="testlarim"),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Testga javob berish", callback_data="tests/submit"
                )
            ],
        ]
    )


def base_menu_keyboards(private_channel_link):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚 SAT Math marafon 10", callback_data="sat_course/info"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Mini kurs",
                    callback_data="courses/intensive_course",
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text="🗂 Vazifaga javob berish",
            #         callback_data="sat_course/send_homework",
            #     )
            # ],
            [
                InlineKeyboardButton(
                    text="✅ Testga javob berish", callback_data="tests/submit"
                )
            ],
            [
                InlineKeyboardButton(text="📜 Testlarim", callback_data="testlarim"),
            ],
        ]
    )
