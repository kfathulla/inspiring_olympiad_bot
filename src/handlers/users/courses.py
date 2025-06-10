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
            text="""⚡️ BEPUL INTENSIV 1.0 KURSi ga xush kelibsiz!

❗️Diqqat bilan o’qing! 

Loyihada ishtirok etish 100% bepul. Faqat, biz tashkil qilayotgan loyiha ko'pchilikka yetib borishi uchun sizning yordamingiz kerak bo'ladi!

Bot sizga maxsus link beradi — 3 nafar do‘stingizni shu link orqali taklif qiling. Ular botga kirib ro‘yxatdan o‘tsa, sizga +1 ball beriladi.

3 ball to‘plaganlar yopiq kanalga qo‘shilib,  10 kun davomida sizlar Milliy Sertifikat, Attestatsiya, DTM va SAT MATH dan natijaga qaratilgan maxsus darslar olib boriladi. 

Keling birga foydali ilm tarqatishni boshlaylik , zero ilm yoyish ham bir baxtdir. 

Quyidagi tugmani bosing va taklif qilishni boshlang 👇""",
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
            text=f"""🎉 “INTENSIV 1.0 KURS”da kimlar va nimalar bo'lishini bilasizmi…

50 dan ortiq Xalqaro Olimpiadachilar , 10.000 da ortiq baxtli talabalar va juda kuchli matematiklar hamda 30 yildan ortiq tajribaga ega Ustozlar tomonidan olib boriladi .

😌" INTENSIV 1.0 KURS " nomli imtihon formatiga asoslangan 10 kunlik BEPUL kursda aynan mana shu MILLIY SERTIFIKAT, ATTESTATSIYA, DTM va SAT MATH imtihonida eng ko'p tushadigna masalalar haqida darslar bo'ladi. 

✅ MILLIY SERTIFIKAT A+      
ATTESTATSIYA 85/100
DTM 30/30
SAT MATH 800/800 — aslida qiyin emas!

Ishtirokchilarga atalgan kitoblar va bonuslar, sovg’alar hamda pul mukofotlari ham bor.

👇Ishtirok etish uchun:

👉🏻 <a href='https://t.me/{me.username}?start={user.user_id}'>Havola ustiga bosing</a> 👈🏻
👉🏻 <a href='https://t.me/{me.username}?start={user.user_id}'>Havola ustiga bosing</a> 👈🏻
👉🏻 <a href='https://t.me/{me.username}?start={user.user_id}'>Havola ustiga bosing</a> 👈🏻""",
disable_web_page_preview=True
        )
        
        await callback.message.answer(text="""Shartlar bilan toʻliq tanishamiz 📌

MILLIY SERTIFIKAT , ATTESTATSIYA, DTM va SAT MATH ga tayyorgarlik ko'rayotgan tanishingizni taklif qilishingiz kerak
    
❗️ Bot sizning uchun alohida taklif havolasi beradi va siz eng kamida 3-ta doʻstingizni taklif qilasiz va siz "INTENSIV 1.0 KURS"da qatnasha olasiz
    
 — Chiqib ketishlarni oldini olish uchun 3 tadan koʻproq odam taklif qilishni maslahat beraman 😉

Bepul kurs, Planshet,kitoblar,  sovg'alar va bonuslar osongina shartga arziydi 💯

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