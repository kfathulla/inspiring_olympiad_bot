from datetime import datetime, timezone
import logging
import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.filters import Command

from typing import List
from src.config import Config
from src.database.models.test_answers import TestAnswer
from src.database.models.tests import Test
from src.database.models.submissions import Submission
from src.database.models.submitted_answers import SubmittedAnswer
from src.database.repo.requests import RequestsRepo
from src.filters.callback.tests.test_action import TestActionCallback
from src.filters.private_chat_filter import PrivateFilter
from src.filters.admins_filter import AdminFilter
from src.database.models.users import User
from src.keyboards.inline.test_submit_cancel import test_cancel_submit_keyboard
from src.keyboards.inline.confirm_test_finish import confirm_test_finish
from src.keyboards.inline.test_cancel_add_scores import test_cancel_add_scores
from src.keyboards.inline.test_initial_menu import test_initial_menu
from src.keyboards.inline.test_list import test_list
from src.keyboards.inline.test_manage_menu import test_manage_menu
from src.keyboards.inline.base_menu import admin_base_menu_keyboards
from src.keyboards.inline.test_cancel_adding_open_answers import (
    test_cancel_adding_open_answers_menu,
)
from src.states.add_test_open_answers import AddTestOpenAnswersState
from src.states.submit_test import SubmitTestState
from src.states.add_test_scores import AddTestScoresState
from src.states.create_test import CreateTestState
from src.utils.misc.excel_utils import generate_test_report

admin_tests_router = Router()


@admin_tests_router.callback_query(
    PrivateFilter(), AdminFilter(), F.data == "tests/add"
)
async def add_test(
    callback: CallbackQuery, state: FSMContext, bot: Bot, repo: RequestsRepo
):
    try:
        text = """➕ Yangi test yaratish

✅ Test nomini kiritib + (plus) belgisini qo'yasiz va barcha kalitni kiritasiz.

✍️ Misol uchun: 
Yangitest+abcdabcdabcd...  yoki
Yangitest+1a2b3c4d5a6b7c...

✅ Katta(A) va kichik(a) harflar bir xil hisoblanadi.
"""
        await state.set_state(CreateTestState.Variants)
        await callback.message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        await callback.answer()
    except Exception as ex:
        logging.error(ex)


@admin_tests_router.message(PrivateFilter(), CreateTestState.Variants)
async def add_test_handler(
    message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo, config: Config
):
    try:
        match = re.match(r"([\w\s]+)\+([\w\d]+)", message.text.strip())
        if not match:
            await message.answer(
                "❌ Invalid format. Please use: TestName+Answers or TestName+1a2b3c"
            )
            return None

        name, test_answers_str = match.groups()
        name = name.strip()

        test = Test(
            user_id=message.from_user.id,
            name=name,
            is_show_correct_count=True,
            is_show_incorrects=True,
            is_show_answers=False,
            is_finished=False,
        )

        test_answers = []
        if any(c.isdigit() for c in test_answers_str):
            matches = re.findall(r"(\d+)([a-zA-Z])", test_answers_str)
            if not matches:
                await message.answer("❌ Invalid numbered format. Use like: 1a2b3c4d")
                return None

            test_answers = [
                {"order": int(num), "text": char.capitalize(), "type": 0, "score": 0}
                for num, char in matches
            ]
        else:
            test_answers = [
                {"order": i + 1, "text": char.capitalize(), "type": 0, "score": 0}
                for i, char in enumerate(test_answers_str)
            ]

        test.answers = [TestAnswer(**answer) for answer in test_answers]

        test = await repo.tests.insert_test(test)
        await state.clear()

        bot_user = await bot.get_me()
        answer_count = len(test.answers)

        res = f"""✅️ Test ishlanishga tayyor
🗒 Test nomi: {test.name}
🔢 Testlar soni: {answer_count} ta
‼️ Test kodi: {test.id}

Test javoblaringizni quyidagi botga jo'nating:

👉 @{bot_user.username}
👉 @{bot_user.username}
👉 @{bot_user.username}

📌 Testda qatnashuvchilar quyidagi ko`rinishda javob yuborishlari mumkin:
Test kodini kiriting va *(yulduzcha) belgisini qo'ying.
To'liq {answer_count} ta javobni ham kiriting.  

Namuna:
{test.id}*abcdab... ({answer_count} ta)   yoki
{test.id}*1a2b3c4d5a6b... ({answer_count} ta)
    
♻️ Test ishlanishga tayyor!!!"""
        await message.answer(text=res, reply_markup=test_initial_menu(test_id=test.id))
    except Exception as ex:
        logging.error(ex)
        await message.answer(
            "❌ Test yaratishda xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "tests/add_open_answers"),
)
async def add_test_open_answers(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)

        text = f"""{test.id}-kodli test uchun ochiq (javobi qo'lda yoziladigan) testlar javobini kiriting. 
Buning uchun javoblarni har birini yangi qatordan, tartib raqamini yozmasdan bittalab yozing.
    
Masalan:  
<code>2,3
4/5
ABC
xato
true
5+7
+
84
...</code>
    
‼️ Eslatma:
1. Ochiq (javobi qo'lda yoziladigan) testlar oldingi testning davomidan qo'shiladi.
    
2. Test topshiruvchi siz qanday shaklda yozgan bo'lsangiz shunday shaklda javob berishi kerak. Masalan: 
<code>4,7 va 4.7
1;5 va 1,5
salom va Salom</code>
belgilari turli xil hisoblanadi.

3. Javoblarda joy qolmasligiga e'tibor bering. Bo'sh joy ham belgi hisoblanadi.
    
4. Agar bu bo'lim kerak bo'lmasa ortga tugmasini bosing."""
        await state.set_state(AddTestOpenAnswersState.Variants)
        await state.update_data(test_id=callback_data.test_id)
        await callback.message.answer(
            text=text, reply_markup=test_cancel_adding_open_answers_menu(test.id)
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "cancel_adding_open_answers"),
)
async def cancel_adding_test_open_answers(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        await state.clear()
        bot_user = await bot.get_me()
        answer_count = len(test.answers)

        await callback.message.delete()
        await callback.message.answer(
            text="Ochiq test qo'shish bekor qilindi.",
            reply_markup=test_initial_menu(test_id=test.id),
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)


@admin_tests_router.message(
    PrivateFilter(), AdminFilter(), AddTestOpenAnswersState.Variants
)
async def add_test_open_answers_handler(
    message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo, config: Config
):
    try:
        state_data = await state.get_data()
        test_id = state_data.get("test_id")
        if not test_id:
            await message.answer(
                "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring."
            )
            return None

        raw_answers = [
            line.strip() for line in message.text.split("\n") if line.strip()
        ]

        if not raw_answers:
            await message.answer("❌ Variantlar kiritilmagan.")
            return None

        test = await repo.tests.get_test_by_id(test_id)
        if not test:
            await message.answer("❌ Test topilmadi.")
            return None

        existing_answers = test.answers or []
        next_order = max([ans.order for ans in existing_answers], default=0) + 1

        new_answers = [
            TestAnswer(
                test_id=test_id, order=next_order + i, text=answer, type=1, score=0
            )
            for i, answer in enumerate(raw_answers)
        ]

        for answer in new_answers:
            await repo.test_answers.add_test_answer(answer)

        bot_user = await bot.get_me()
        answer_count = len(existing_answers) + len(new_answers)

        res = f"""✅️ Test ishlanishga tayyor
🗒 Test nomi: {test.name}
🔢 Testlar soni: {answer_count} ta
‼️ Test kodi: {test.id}

Test javoblaringizni quyidagi botga jo'nating:

👉 @{bot_user.username}
👉 @{bot_user.username}
👉 @{bot_user.username}

📌 Testda qatnashuvchilar quyidagi ko`rinishda javob yuborishlari mumkin:
Test kodini kiriting va *(yulduzcha) belgisini qo'ying.
To'liq {answer_count} ta javobni ham kiriting.  

Namuna:
<code>{test.id}*abcdab... 
7
1/2
3-1</code>
    
♻️ Test ishlanishga tayyor!!!"""
        await message.answer(text=res, reply_markup=test_initial_menu(test_id=test.id))
        await state.clear()
    except Exception as ex:
        logging.error(ex)
        await message.answer(
            "❌ Test yaratishda xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "manage")
)
async def manage_test(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        answer_lines = []
        for i, answer in enumerate(test.answers, start=1):
            if answer.type == 0:
                answer_line = f"{i}. {answer.text}"
            else:
                answer_line = f"{i}. {answer.text}"

            answer_lines.append(answer_line)

        response = (
            f"{test.id}-test javoblari:\n<code>"
            + "\n".join(answer_lines)
            + "</code>\nAgar test uchun ball qo'shishni xohlasangiz ball qo'shish tugmasini bosing."
        )
        await callback.message.answer(
            text=response,
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            ),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "switch_show_correct_count"),
)
async def switch_show_correct_count(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        await repo.tests.update_test(
            test, is_show_correct_count=not test.is_show_correct_count
        )

        await callback.message.edit_reply_markup(
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            )
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "switch_show_incorrects"),
)
async def switch_show_incorrects(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        await repo.tests.update_test(
            test, is_show_incorrects=not test.is_show_incorrects
        )

        await callback.message.edit_reply_markup(
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            )
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "switch_show_answers"),
)
async def switch_show_answers(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        await repo.tests.update_test(test, is_show_answers=not test.is_show_answers)

        await callback.message.edit_reply_markup(
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            )
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "add_scores")
)
async def add_scores(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        text = f"""{test.id}-testga ball qo'shish uchun 
✅️1.1;1.1;2.1.... ko'rinishida ballarni jo'nating. 
       
✅️o'nli kasrni . bilan bering, orasi ; bilan bering. Oxiriga ; qo'ymang.

✅️Barcha test uchun ball kiriting."""
        await state.set_state(AddTestScoresState.Scores)
        await state.update_data(test_id=callback_data.test_id)
        await callback.message.answer(
            text=text, reply_markup=test_cancel_add_scores(test.id)
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.message(PrivateFilter(), AdminFilter(), AddTestScoresState.Scores)
async def add_scores_handler(
    message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo
):
    try:
        test = await repo.tests.get_test_by_id(await state.get_value("test_id"))
        if not test:
            await message.answer("❌ Test topilmadi.")
            return None

        scores = [float(score) for score in message.text.split(";") if score]
        if len(test.answers) != len(scores):
            await message.answer(
                text="Ball kiritishda xatolik. 🚫 \n‼️Test soni va ball soni teng emas.",
                reply_markup=test_cancel_add_scores(test.id),
            )
            return None

        for answer, score in zip(test.answers, scores):
            await repo.test_answers.update_test_answer(answer, score=score)

        total_score = sum(answer.score for answer in test.answers)
        answer_lines = [
            f"{i+1}. {answer.text} {answer.score} ball"
            for i, answer in enumerate(test.answers)
        ]

        answers_section = "\n".join(answer_lines)
        response = f"""✅️ {test.id}-testga ballar qo'shildi
    
🗒 Test nomi: {test.name}
🔢 Testlar soni: {len(test.answers)} ta
🧮 Test ballari: 
{answers_section}

Jami: {total_score:.2f} ball
    
✅️ Testga ball qo'shildi."""
        await message.answer(
            text=response,
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            ),
        )

        await state.clear()
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "cancel_add_scores"),
)
async def cancel_add_scores(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        await state.clear()

        await callback.message.delete()
        await callback.message.answer(text="Ball qo'shish bekor qilindi.")

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "finish")
)
async def finish(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None
        await callback.message.delete()
        await callback.message.answer(
            text=f"{test.id} kodli testni haqiqatdan tugatmoqchimisiz ⁉️",
            reply_markup=confirm_test_finish(test.id),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "confirm_finish"),
)
async def confirm_finish(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        await repo.tests.update_test(test, is_finished=True, finished_at=datetime.now())

        answer_lines = []
        for i, answer in enumerate(test.answers, start=1):
            if answer.type == 0:
                answer_line = f"{i}. {answer.text}"
            else:
                answer_line = f"{i}. {answer.text}"

            answer_lines.append(answer_line)

        response = (
            f"{test.id}-test javoblari:\n<code>"
            + "\n".join(answer_lines)
            + "</code>\nAgar test uchun ball qo'shishni xohlasangiz ball qo'shish tugmasini bosing."
        )
        await callback.message.delete()
        await callback.message.answer("Test tugatildi.")
        await callback.message.answer(
            text=response,
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            ),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(),
    AdminFilter(),
    TestActionCallback.filter(F.action == "cancel_finish"),
)
async def cancel_finish(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        answer_lines = []
        for i, answer in enumerate(test.answers, start=1):
            if answer.type == 0:
                answer_line = f"{i}. {answer.text}"
            else:
                answer_line = f"{i}. {answer.text}"

            answer_lines.append(answer_line)

        response = (
            f"{test.id}-test javoblari:\n<code>"
            + "\n".join(answer_lines)
            + "</code>\nAgar test uchun ball qo'shishni xohlasangiz ball qo'shish tugmasini bosing."
        )
        await callback.message.delete()
        await callback.message.answer(
            text=response,
            reply_markup=test_manage_menu(
                test_id=test.id,
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers,
            ),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(
    PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "info")
)
async def info(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None

        submissions = await repo.submissions.get_submissions_by_test(test.id)
        excel_file = await generate_test_report(test, submissions)
        await callback.message.answer_document(
            document=excel_file, caption=f"Test #{test.id} Natijalari"
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.message(PrivateFilter(), Command("submit_by_admin"))
async def submit_test(
    message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo
):
    try:
        text = """❗️ Testga javob berish

✅ Test kodini kiritib * (yulduzcha) belgisini qo'yasiz va barcha kalitlarni kiritasiz.

✍️ Misol uchun: 
user_id*123*abcdabcdabcd...  yoki
123*123*1a2b3c4d5a6b7c...

⁉️ Testga faqat bir marta javob berish mumkin.

✅ Katta(A) va kichik(a) harflar bir xil hisoblanadi."""
        await state.set_state(SubmitTestState.Answer)
        await message.answer(
            text=text, reply_markup=test_cancel_submit_keyboard
        )
    except Exception as ex:
        logging.error(ex)
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.callback_query(PrivateFilter(), F.data == "test_cancel_submit")
async def test_cancel_submit(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    user: User,
    repo: RequestsRepo,
    config: Config,
):
    try:
        await state.clear()
        await callback.message.answer(
            text="Quyidagilardan birini tanlang! 👇",
            reply_markup=(admin_base_menu_keyboards(user.private_channel_link)),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@admin_tests_router.message(PrivateFilter(), SubmitTestState.Answer)
async def submit_test_handler(
    message: Message, state: FSMContext, repo: RequestsRepo
):
    try:
        parts = message.text.split("\n", 1)
        if not parts or "*" not in parts[0] or "*" not in parts[1]:
            await message.answer("Test javobini noto'g'ri formatda kiritdingiz.")
            return

        user_id_part, test_id_part, closed_answer_part = parts[0].split("*", 2)
        test_id = int(test_id_part.strip())
        user_id = int(user_id_part.strip())

        old_submissions = await repo.submissions.get_user_submissions_by_test(
            user_id, test_id
        )
        if old_submissions is not None and len(old_submissions) > 0:
            await message.answer(
                "‼️ Bu testga siz javob berib boʻlgansiz!\n\n‼️ Bitta testga faqat bir marta javob berish mumkin"
            )
            return

        user = await repo.users.get_by_id(user_id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            return
    
        test = await repo.tests.get_test_by_id(test_id)
        if not test:
            await message.answer("❌ Test topilmadi.")
            return

        if test.is_finished:
            await message.answer("‼️ Bu testga javob jo'natish tugagan.")
            return

        if any(c.isdigit() for c in closed_answer_part):
            submitted_closed_answers = []
            pairs = re.findall(r"(\d+)([a-zA-Z])", closed_answer_part)
            for num, char in pairs:
                try:
                    submitted_closed_answers.append((int(num), char.capitalize()))
                except ValueError:
                    continue
            if not submitted_closed_answers:
                raise ValueError("Invalid numbered answer format")
        else:
            submitted_closed_answers = [
                (i + 1, char.capitalize())
                for i, char in enumerate(closed_answer_part)
                if char.isalpha()
            ]

        submitted_open_answers = []
        if len(parts) > 2:
            submitted_open_answers = [
                (i + 1, line.strip())
                for i, line in enumerate(parts[2].split("\n"))
                if line.strip()
            ]

        closed_answers = [a for a in test.answers if a.type == 0]
        if len(submitted_closed_answers) != len(closed_answers):
            await message.answer(
                f"❌ {test.id} raqamli testda {len(closed_answers)} ta yopiq test bor. \n❓️ Siz esa {len(submitted_closed_answers)} ta yopiq javob jo'natdingiz.\n♻️ Iltimos qayta sanab chiqing."
            )
            return

        open_answers = [a for a in test.answers if a.type == 1]
        if len(open_answers) != 0 and len(submitted_open_answers) != len(open_answers):
            await message.answer(
                f"❌ {test.id} raqamli testda {len(open_answers)} ta ochiq test bor. \n❓️ Siz esa {len(submitted_open_answers)} ta yopiq javob jo'natdingiz.\n♻️ Iltimos qayta sanab chiqing."
            )
            return

        correct_count = 0
        total_score = 0
        submitted_answers: List[SubmittedAnswer] = []

        for sa, ca in zip(submitted_closed_answers, closed_answers):
            is_correct = sa[1] == ca.text
            if is_correct:
                correct_count += 1
                total_score += ca.score

            submitted_answers.append(
                SubmittedAnswer(
                    text=sa[1],
                    test_answer_id=ca.id,
                    test_answer=ca,
                    is_correct=is_correct,
                    score=(ca.score if is_correct else 0),
                )
            )

        for sa, ca in zip(submitted_open_answers, open_answers):
            is_correct = sa[1] == ca.text
            if is_correct:
                correct_count += 1
                total_score += ca.score

            submitted_answers.append(
                SubmittedAnswer(
                    text=sa[1],
                    test_answer_id=ca.id,
                    test_answer=ca,
                    is_correct=is_correct,
                    score=ca.score if is_correct else 0,
                )
            )

        percentage = (
            (correct_count / len(test.answers)) * 100 if len(test.answers) > 0 else 0
        )
        await repo.submissions.add_submission(
            submission=Submission(
                text=message.text,
                correct_count=correct_count,
                incorrect_count=len(test.answers) - correct_count,
                score=total_score,
                user_id=user_id,
                test_id=test.id,
                submitted_answers=submitted_answers,
            )
        )
        await state.clear()

        summary = f"""\n\n📊 Jami: {correct_count} ta ({percentage:.2f}%)"""
        header = f"""🏆 <a href="t.me/{user.username}">{user.full_name}</a> ning natijasi

📌 Test kodi: {test.id}
📋 Savollar soni: {len(test.answers)} ta"""
        if not test.is_show_correct_count:
            await message.answer(text="Javobingiz qabul qilindi")
            return

        if not test.is_show_incorrects:
            await message.answer(text=header + summary, disable_web_page_preview=True)
            return

        answers_lines = []
        for i, answer in enumerate(submitted_answers, 1):
            if test.is_show_answers:
                correct_mark = (
                    f"✅  {answer.score} ball"
                    if answer.is_correct
                    else f"❌ ({answer.test_answer.text})   0 ball"
                )
            else:
                correct_mark = f"✅  {answer.score} ball" if answer.is_correct else "❌"

            answers_lines.append(f"{i}. {answer.text} {correct_mark}")

        response = header + "\n\nNatijalari:\n" + "\n".join(answers_lines) + summary

        await message.answer(response, disable_web_page_preview=True)

    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")
