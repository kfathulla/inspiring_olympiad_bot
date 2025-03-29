from datetime import datetime, timezone
import logging
import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from src.config import Config
from src.database.models.test_answers import TestAnswer
from src.database.models.tests import Test
from src.database.repo.requests import RequestsRepo
from src.filters.callback.tests.test_action import TestActionCallback
from src.filters.private_chat_filter import PrivateFilter
from src.filters.admins_filter import AdminFilter

from src.keyboards.inline.confirm_test_finish import confirm_test_finish
from src.keyboards.inline.base_menu import admin_base_menu_keyboards
from src.keyboards.inline.test_cancel_add_scores import test_cancel_add_scores
from src.keyboards.inline.test_initial_menu import test_initial_menu
from src.keyboards.inline.test_list import test_list
from src.keyboards.inline.test_manage_menu import test_manage_menu
from src.keyboards.inline.test_cancel_adding_open_answers import test_cancel_adding_open_answers_menu
from src.states.add_test_open_answers import AddTestOpenAnswersState
from src.states.add_test_scores import AddTestScoresState
from src.states.create_test import CreateTestState

admin_tests_router = Router()

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), F.data == "tests/add")
async def add_test(callback: CallbackQuery, state: FSMContext, bot: Bot, repo: RequestsRepo):
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
async def add_test_handler(message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo, config: Config):
    try:
        match = re.match(r"([\w\s]+)\+([\w\d]+)", message.text.strip())
        if not match:
            await message.answer("❌ Invalid format. Please use: TestName+Answers or TestName+1a2b3c")
            return None

        name, test_answers_str = match.groups()
        name = name.strip()
        
        test = Test(
            user_id=message.from_user.id,
            name=name,
            is_show_correct_count=True,
            is_show_incorrects=True,
            is_show_answers=False,
            is_finished=False
        )

        test_answers = []
        if any(c.isdigit() for c in test_answers_str):
            matches = re.findall(r'(\d+)([a-zA-Z])', test_answers_str)
            if not matches:
                await message.answer("❌ Invalid numbered format. Use like: 1a2b3c4d")
                return None

            test_answers = [
                {"order": int(num), "text": char.capitalize(), "type": 0, "score": 0} 
                for num, char in matches
            ]
        else:  
            test_answers = [
                {"order": i + 1, "text": char.capitalize(), "type": 0, "score": 0 } 
                for i, char in enumerate(test_answers_str)
            ]
            
        test.test_answers = [TestAnswer(**answer) for answer in test_answers]
        
        test = await repo.tests.insert_test(test)
        await state.clear()

        bot_user = await bot.get_me()
        answer_count = len(test.test_answers)
        
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
        await message.answer("❌ Test yaratishda xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "tests/add_open_answers"))
async def add_test_open_answers(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
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
        await callback.message.answer(text=text, reply_markup=test_cancel_adding_open_answers_menu(test.id))
        await callback.answer()
    except Exception as ex:
        logging.error(ex)

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "cancel_adding_open_answers"))
async def cancel_adding_test_open_answers(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        await state.clear()
        bot_user = await bot.get_me()
        answer_count = len(test.test_answers)

        await callback.message.delete()
        await callback.message.answer(text="Ochiq test qo'shish bekor qilindi.", reply_markup=test_initial_menu(test_id=test.id))
        await callback.answer()
    except Exception as ex:
        logging.error(ex)

@admin_tests_router.message(PrivateFilter(), AdminFilter(), AddTestOpenAnswersState.Variants)
async def add_test_open_answers_handler(message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo, config: Config):
    try:
        state_data = await state.get_data()
        test_id = state_data.get('test_id')
        if not test_id:
            await message.answer("❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
            return None

        raw_answers = [line.strip() for line in message.text.split('\n') if line.strip()]

        if not raw_answers:
            await message.answer("❌ Variantlar kiritilmagan.")
            return None

        test = await repo.tests.get_test_by_id(test_id)
        if not test:
            await message.answer("❌ Test topilmadi.")
            return None

        existing_answers = test.test_answers or []
        next_order = max([ans.order for ans in existing_answers], default=0) + 1

        new_answers = [
            TestAnswer(
                test_id=test_id,
                order=next_order + i,
                text=answer,
                type=1,
                score=0
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
        await message.answer("❌ Test yaratishda xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "manage"))
async def manage_test(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None            

        answer_lines = []
        for i, answer in enumerate(test.test_answers, start=1):
            if answer.type == 0:
                answer_line = f"{i}. {answer.text}"
            else:
                answer_line = f"{i}. {answer.text}"
            
            answer_lines.append(answer_line)
            
        response = f"{test.id}-test javoblari:\n<code>" + "\n".join(answer_lines) + "</code>\nAgar test uchun ball qo'shishni xohlasangiz ball qo'shish tugmasini bosing."
        await callback.message.answer(
            text=response, 
            reply_markup=test_manage_menu(
                test_id=test.id, 
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "switch_show_correct_count"))
async def switch_show_correct_count(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   

        await repo.tests.update_test(test, is_show_correct_count=not test.is_show_correct_count)
        
        await callback.message.edit_reply_markup(reply_markup=test_manage_menu(
            test_id=test.id, 
            is_show_correct_count=test.is_show_correct_count,
            is_show_incorrects=test.is_show_incorrects,
            is_show_answers=test.is_show_answers))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "switch_show_incorrects"))
async def switch_show_incorrects(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   

        await repo.tests.update_test(test, is_show_incorrects=not test.is_show_incorrects)
        
        await callback.message.edit_reply_markup(reply_markup=test_manage_menu(
            test_id=test.id, 
            is_show_correct_count=test.is_show_correct_count,
            is_show_incorrects=test.is_show_incorrects,
            is_show_answers=test.is_show_answers))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "switch_show_answers"))
async def switch_show_answers(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   

        await repo.tests.update_test(test, is_show_answers=not test.is_show_answers)
        
        await callback.message.edit_reply_markup(reply_markup=test_manage_menu(
            test_id=test.id, 
            is_show_correct_count=test.is_show_correct_count,
            is_show_incorrects=test.is_show_incorrects,
            is_show_answers=test.is_show_answers))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "add_scores"))
async def add_scores(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
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
        await callback.message.answer(text=text, reply_markup=test_cancel_add_scores(test.id))                 
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.message(PrivateFilter(), AdminFilter(), AddTestScoresState.Scores)
async def add_scores_handler(message: Message, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(await state.get_value("test_id"))
        if not test:
            await message.answer("❌ Test topilmadi.")
            return None   

        scores = [float(score) for score in message.text.split(';') if score]
        if len(test.test_answers) != len(scores):
            await message.answer(text="Ball kiritishda xatolik. 🚫 \n‼️Test soni va ball soni teng emas.", reply_markup=test_cancel_add_scores(test.id))      
            return None

        for answer, score in zip(test.test_answers, scores):
            await repo.test_answers.update_test_answer(answer, score=score)

        total_score = sum(answer.score for answer in test.test_answers)
        answer_lines = [
            f"{i+1}. {answer.text} {answer.score} ball"
            for i, answer in enumerate(test.test_answers)
        ]
        
        answers_section = '\n'.join(answer_lines)
        response = f"""✅️ {test.id}-testga ballar qo'shildi
    
🗒 Test nomi: {test.name}
🔢 Testlar soni: {len(test.test_answers)} ta
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
                is_show_answers=test.is_show_answers))     
                 
        await state.clear()
    except Exception as ex:
        logging.error(ex)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "cancel_add_scores"))
async def cancel_add_scores(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
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
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "finish"))
async def finish(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   
        await callback.message.delete()
        await callback.message.answer(
            text=f"{test.id} kodli testni haqiqatdan tugatmoqchimisiz ⁉️",
            reply_markup=confirm_test_finish(test.id))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "confirm_finish"))
async def confirm_finish(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   

        await repo.tests.update_test(test, is_finished=True, finished_at=datetime.now())

        answer_lines = []
        for i, answer in enumerate(test.test_answers, start=1):
            if answer.type == 0:
                answer_line = f"{i}. {answer.text}"
            else:
                answer_line = f"{i}. {answer.text}"
            
            answer_lines.append(answer_line)
            
        response = f"{test.id}-test javoblari:\n<code>" + "\n".join(answer_lines) + "</code>\nAgar test uchun ball qo'shishni xohlasangiz ball qo'shish tugmasini bosing."
        await callback.message.delete()
        await callback.message.answer("Test tugatildi.")
        await callback.message.answer(
            text=response, 
            reply_markup=test_manage_menu(
                test_id=test.id, 
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "cancel_finish"))
async def cancel_finish(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   

        answer_lines = []
        for i, answer in enumerate(test.test_answers, start=1):
            if answer.type == 0:
                answer_line = f"{i}. {answer.text}"
            else:
                answer_line = f"{i}. {answer.text}"
            
            answer_lines.append(answer_line)
            
        response = f"{test.id}-test javoblari:\n<code>" + "\n".join(answer_lines) + "</code>\nAgar test uchun ball qo'shishni xohlasangiz ball qo'shish tugmasini bosing."
        await callback.message.delete() 
        await callback.message.answer(
            text=response, 
            reply_markup=test_manage_menu(
                test_id=test.id, 
                is_show_correct_count=test.is_show_correct_count,
                is_show_incorrects=test.is_show_incorrects,
                is_show_answers=test.is_show_answers))
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")

@admin_tests_router.callback_query(PrivateFilter(), AdminFilter(), TestActionCallback.filter(F.action == "info"))
async def info(callback: CallbackQuery, callback_data: TestActionCallback, state: FSMContext, bot: Bot, repo: RequestsRepo):
    try:
        test = await repo.tests.get_test_by_id(callback_data.test_id)
        if not test:
            await callback.message.answer("❌ Test topilmadi.")
            return None   
   
        
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring.")
