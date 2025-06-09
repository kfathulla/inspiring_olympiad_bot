import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from src.config import Config
from src.filters.private_chat_filter import PrivateFilter
from src.keyboards.inline.base_menu import (
    base_menu_keyboards,
    admin_base_menu_keyboards,
)
from src.keyboards.inline.mini_course_menu import mini_course_menu_keyboards
from src.database.models.users import User


courses_router = Router()

@courses_router.callback_query(PrivateFilter(), F.data == "courses/intensive_course")
async def intensive_course(callback: CallbackQuery, user: User, config: Config):
    try:
        await callback.message.answer(
            text="Mini kurs haqida ma'lumot tez orada joylanadi.",
            reply_markup=mini_course_menu_keyboards(user.private_channel_link)
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )
        
@courses_router.callback_query(PrivateFilter(), F.data == "courses/intensive_course/referral_post")
async def intensive_course_referral_post(callback: CallbackQuery, user: User, config: Config, bot: Bot):
    try:
        me = await bot.get_me()
        await callback.message.answer(
            text=f"""🎉 “Mini kurs”da kimlar va nimalar bo'lishini bilasizmi…

Prezident Maktabida 79ta, Al-Xorazmiy maktabiga 29ta va Ixtisoslashtirilgan maktablarga 300+ o'quvchilari kirgan ustozlar.

😌"Mini kurs" nomli imtihon formatiga asoslangan 1 haftalik BEPUL kursda aynan mana shu maktablar imtihonida eng ko'p tushadigna masalalar haqida darslar bo'ladi. 

✅ Tanqidiy Fikrlash, Mantiqiy Masalalar va Ingliz tili — aslida qiyin emas!

Ishtirokchilarga atalgan kitoblar va bonuslar, sovg’alar ham bor.

👇Ishtirok etish uchun:

👉🏻 <a href='https://t.me/{me.username}?start={user.user_id}'>Havola ustiga bosing</a> 👈🏻
👉🏻 <a href='https://t.me/{me.username}?start={user.user_id}'>Havola ustiga bosing</a> 👈🏻
👉🏻 <a href='https://t.me/{me.username}?start={user.user_id}'>Havola ustiga bosing</a> 👈🏻""",
disable_web_page_preview=True
        )
        
        await callback.message.answer(text="""Shartlar bilan toʻliq tanishamiz 📌

Prezident, Al-Xorazmiy va ixtisoslashgan maktabga tayyorgarlik ko'rayotgan tanishingizni taklif qilishingiz kerak
    
❗️ Bot sizning uchun alohida taklif havolasi beradi va siz eng kamida 5-ta doʻstingizni taklif qilasiz va siz "Mini Kurs"da qatnasha olasiz
    
 — Chiqib ketishlarni oldini olish uchun 5tadan koʻproq odam taklif qilishni maslahat beraman 😉

Bepul kurs, Planshet, sovg'alar va bonuslar osongina shartga arziydi 💯

Tayyor boʻlsangiz hoziroq yuqoridagi postni tarqatib do'stlarni taklif qilishni boshlang."""
)
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )
        
@courses_router.callback_query(PrivateFilter(), F.data == "courses/intensive_course/referral_ball")
async def intensive_course_referral_ball(callback: CallbackQuery, user: User, config: Config):
    try:
        await callback.message.answer(
            text=f"""📈Sizning ballaringiz: {user.referral_count} ball. 

‼️Sizning havolangiz orqali kirgan odam kanallarimizdan chiqib ketsa balingiz kamayishi mumkin.""",
            reply_markup=mini_course_menu_keyboards(user.private_channel_link)
        )
        await callback.answer()
    except Exception as ex:
        logging.error(ex)
        await callback.message.answer(
            "❌ Xatolik yuz berdi. Iltimos qaytatdan urinib ko'ring."
        )