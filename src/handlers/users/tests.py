import logging
import re
from typing import List
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command

from src.config import Config
from src.database.models.submissions import Submission
from src.database.models.users import User
from src.database.models.submitted_answers import SubmittedAnswer
from src.database.repo.requests import RequestsRepo
from src.filters.private_chat_filter import PrivateFilter
from src.filters.callback.tests.test_action import TestActionCallback
from src.keyboards.inline.test_submit_cancel import test_cancel_submit_keyboard
from src.states.submit_test import SubmitTestState
from src.keyboards.inline.base_menu import (
    admin_base_menu_keyboards,
    base_menu_keyboards,
)

from src.keyboards.inline.test_list import test_list
from src.keyboards.inline.submission_list import submission_list

tests_router = Router()


@tests_router.callback_query(PrivateFilter(), F.data == "tests/submit")
async def submit_test(
    callback: CallbackQuery, state: FSMContext, bot: Bot, repo: RequestsRepo
):
    try:
        text = """❗️ Testga javob berish

✅ Test kodini kiritib * (yulduzcha) belgisini qo'yasiz va barcha kalitlarni kiritasiz.

✍️ Misol uchun: 
123*abcdabcdabcd...  yoki
123*1a2b3c4d5a6b7c...

⁉️ Testga faqat bir marta javob berish mumkin.

✅ Katta(A) va kichik(a) harflar bir xil hisoblanadi."""
        await state.set_state(SubmitTestState.Answer)
        await callback.message.answer(
            text=text, reply_markup=test_cancel_submit_keyboard
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@tests_router.callback_query(PrivateFilter(), F.data == "test_cancel_submit")
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
            reply_markup=(
                admin_base_menu_keyboards(user.private_channel_link)
                if callback.from_user.id in config.tg_bot.admin_ids
                else base_menu_keyboards(user.private_channel_link)
            ),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@tests_router.message(PrivateFilter(), SubmitTestState.Answer)
async def submit_test_handler(
    message: Message, state: FSMContext, user: User, repo: RequestsRepo
):
    try:
        parts = message.text.split("\n", 1)
        if not parts or "*" not in parts[0]:
            await message.answer("Test javobini noto'g'ri formatda kiritdingiz.")
            return

        test_id_part, closed_answer_part = parts[0].split("*", 1)
        test_id = int(test_id_part.strip())

        old_submissions = await repo.submissions.get_user_submissions_by_test(
            user.user_id, test_id
        )
        if old_submissions is not None and len(old_submissions) > 0:
            await message.answer(
                "‼️ Bu testga siz javob berib boʻlgansiz!\n\n‼️ Bitta testga faqat bir marta javob berish mumkin"
            )
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
        if len(parts) > 1:
            submitted_open_answers = [
                (i + 1, line.strip())
                for i, line in enumerate(parts[1].split("\n"))
                if line.strip()
            ]

        test = await repo.tests.get_test_by_id(test_id)
        if not test:
            await message.answer("❌ Test topilmadi.")
            return

        closed_answers = [a for a in test.answers if a.type == 0]
        if len(submitted_closed_answers) != len(closed_answers):
            await message.answer(
                f"❌ {test.id} raqamli testda {len(closed_answers)} ta yopiq test bor. \n❓️ Siz esa {len(submitted_closed_answers)} ta yopiq javob jo'natdingiz.\n♻️ Iltimos qayta sanab chiqing."
            )
            return

        open_answers = [a for a in test.answers if a.type == 1]
        if len(open_answers) != 0 and len(submitted_open_answers) != len(
            open_answers
        ):
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
            (correct_count / len(test.answers)) * 100
            if len(test.answers) > 0
            else 0
        )
        await repo.submissions.add_submission(
            submission=Submission(
                text=message.text,
                correct_count=correct_count,
                incorrect_count=len(test.answers) - correct_count,
                score=total_score,
                user_id=user.user_id,
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
                correct_mark = (
                    f"✅  {answer.score} ball" if answer.is_correct else "❌   0 ball"
                )

            answers_lines.append(f"{i}. {answer.text} {correct_mark}")

        response = header + "\n\nNatijalari:\n" + "\n".join(answers_lines) + summary

        await message.answer(response, disable_web_page_preview=True)

    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")


@tests_router.callback_query(PrivateFilter(), F.data == "testlarim")
async def tests(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    repo: RequestsRepo,
    config: Config,
):
    try:
        if callback.from_user.id in config.tg_bot.admin_ids:
            tests = await repo.tests.get_tests_by_user(callback.from_user.id)
            if not tests:
                await callback.message.answer("❌ Testlar topilmadi.")
                await callback.answer()
                return None

            await callback.message.answer(
                text="🔍 Siz yaratgan quyidagi testlar topildi:\n\n⌛️ - Faol testlar \n⛔️ - Yakunlangan testlar",
                reply_markup=test_list(tests),
            )

        submissions = await repo.submissions.get_submissions_by_user(
            callback.from_user.id
        )
        await callback.message.answer(
            text="🔍 Siz yechgan quyidagi testlar topildi:\n\n⌛️ - Faol testlar \n⛔️ - Yakunlangan testlar",
            reply_markup=submission_list(submissions),
        )

        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )


@tests_router.message(PrivateFilter(), Command("testlarim"))
async def tests(
    message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo, config: Config
):
    try:
        if message.from_user.id in config.tg_bot.admin_ids:
            tests = await repo.tests.get_tests_by_user(message.from_user.id)
            if not tests:
                await message.answer("❌ Testlar topilmadi.")
                return None

            await message.answer(
                text="🔍 Siz yaratgan quyidagi testlar topildi:\n\n⌛️ - Faol testlar \n⛔️ - Yakunlangan testlar",
                reply_markup=test_list(tests),
            )

        submissions = await repo.submissions.get_submissions_by_user(
            message.from_user.id
        )
        await message.answer(
            text="🔍 Siz yechgan quyidagi testlar topildi:\n\n⌛️ - Faol testlar \n⛔️ - Yakunlangan testlar",
            reply_markup=submission_list(submissions),
        )
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")


@tests_router.callback_query(
    PrivateFilter(), TestActionCallback.filter(F.action == "my_result")
)
async def my_result(
    callback: CallbackQuery,
    callback_data: TestActionCallback,
    state: FSMContext,
    bot: Bot,
    user: User,
    repo: RequestsRepo,
):
    try:
        submission = (
            await repo.submissions.get_user_submissions_by_test(
                user_id=callback.from_user.id, test_id=callback_data.test_id
            )
        )[0]
        submission.test.answers = await repo.test_answers.get_test_answers_by_test(submission.test_id)
        submission.submitted_answers = await repo.submitted_answers.get_submitted_answers_by_submission(submission.id)
        percentage = (
            (submission.correct_count / len(submission.test.answers)) * 100
            if len(submission.test.answers) > 0
            else 0
        )
        summary = f"""\n\n📊 Jami: {submission.correct_count} ta ({percentage:.2f}%)"""
        header = f"""🏆 <a href="t.me/{user.username}">{user.full_name}</a> ning natijasi

📌 Test kodi: {submission.test_id}
📋 Savollar soni: {len(submission.test.answers)} ta"""
        if not submission.test.is_show_correct_count:
            await callback.message.answer(text="Javobingiz qabul qilingan")
            return

        if not submission.test.is_show_incorrects:
            await callback.message.answer(text=header + summary, disable_web_page_preview=True)
            await callback.answer()
            return

        answers_lines = []
        for i, answer in enumerate(submission.submitted_answers, 1):
            if submission.test.is_show_answers:
                correct_mark = (
                    f"✅  {answer.score} ball"
                    if answer.is_correct
                    else f"❌ ({answer.test_answer.text})   0 ball"
                )
            else:
                correct_mark = (
                    f"✅  {answer.score} ball" if answer.is_correct else "❌   0 ball"
                )

            answers_lines.append(f"{i}. {answer.text} {correct_mark}")

        response = header + "\n\nNatijalari:\n" + "\n".join(answers_lines) + summary

        await callback.message.answer(response, disable_web_page_preview=True)
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")
