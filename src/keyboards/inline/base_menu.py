from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_base_menu_keyboards(private_channel_link):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🥇 May olimpiadasi", callback_data="olympiad/may"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 SAT Math marafon 10", callback_data="sat_course/info"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Grandlar olimpiadasi 20 MILLION",
                    callback_data="olympiad/grands",
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
                    text="🥇 May olimpiadasi", callback_data="olympiad/may"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 SAT Math marafon 10", callback_data="sat_course/info"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Grandlar olimpiadasi 20 MILLION",
                    callback_data="olympiad/grands",
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
