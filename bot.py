# -*- coding: utf-8 -*-
"""
Test Bot — guruh a'zolaridan test yechuvchilarni so'raydigan
va ishtirok etganlarga avtomatik test tashlaydigan bot.

Ishlash tartibi:
1. Guruhda kimdir /test deb yozadi.
2. Bot fanlar ro'yxatini tugmalar bilan chiqaradi.
3. Fanni bosgan odam botning shaxsiy chatiga o'tkaziladi (deep link orqali)
   va u yerda test avtomatik boshlanadi.
4. Har bir savol Telegramning o'z "Quiz Poll" formatida yuboriladi.
5. Test tugagach, natija chiqadi va scores.json faylga yoziladi.
6. Guruhda /reyting buyrug'i bilan TOP-10 ko'rsatiladi.
"""

import asyncio
import json
import os
import random
import logging
import threading
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, PollAnswer
from aiogram.enums import ParseMode
from flask import Flask

import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

SCORES_FILE = "scores.json"

# Foydalanuvchining faol test holati: {user_id: {...}}
active_sessions = {}
# Qaysi poll kimga tegishli ekanini bilish uchun: {poll_id: user_id}
poll_owner = {}


def load_scores():
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


@dp.message(CommandStart(deep_link=True))
async def start_with_payload(message: Message, command: CommandObject):
    subject_key = command.args
    if subject_key not in QUESTIONS:
        await message.answer("Bu test topilmadi. Guruhda /test buyrug'ini qayta bosing.")
        return
    await boshla_test(message.from_user.id, message.from_user.full_name, subject_key)


@dp.message(CommandStart())
async def start_plain(message: Message):
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Bu bot orqali fanlardan test yecha olasiz.\n"
        "Guruhda <b>/test</b> deb yozing va fanni tanlang.",
        parse_mode=ParseMode.HTML,
    )


@dp.message(Command("test"))
async def test_command(message: Message):
    rows = []
    for key, subject in QUESTIONS.items():
        url = f"https://t.me/{config.BOT_USERNAME}?start={key}"
        rows.append([InlineKeyboardButton(text=f"📘 {subject['nomi']}", url=url)])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    await message.answer(
        "📝 <b>Test vaqti!</b>\n\n"
        "Kim test yechmoqchi bo'lsa, fanni tanlasin — bot shaxsiy chatda "
        "avtomatik test tashlaydi:",
        reply_markup=kb,
        parse_mode=ParseMode.HTML,
    )


async def boshla_test(user_id: int, full_name: str, subject_key: str):
    subject = QUESTIONS[subject_key]
    barcha_savollar = subject["savollar"]
    soni = min(config.SAVOLLAR_SONI, len(barcha_savollar))
    tanlangan = random.sample(barcha_savollar, soni)

    active_sessions[user_id] = {
        "subject_key": subject_key,
        "subject_nomi": subject["nomi"],
        "full_name": full_name,
        "savollar": tanlangan,
        "index": 0,
        "togri_soni": 0,
        "boshlandi": datetime.now().isoformat(),
    }

    await bot.send_message(
        user_id,
        f"🎯 <b>{subject['nomi']}</b> fanidan {soni} ta savoldan iborat test boshlandi!\nOmad!",
        parse_mode=ParseMode.HTML,
    )
    await keyingi_savol(user_id)


async def keyingi_savol(user_id: int):
    session = active_sessions.get(user_id)
    if not session:
        return

    idx = session["index"]
    savollar = session["savollar"]

    if idx >= len(savollar):
        await testni_yakunla(user_id)
        return

    savol = savollar[idx]
    poll = await bot.send_poll(
        chat_id=user_id,
        question=f"{idx + 1}) {savol['savol']}",
        options=savol["variantlar"],
        type="quiz",
        correct_option_id=savol["togri"],
        is_anonymous=False,
    )
    poll_owner[poll.poll.id] = user_id


@dp.poll_answer()
async def poll_answer_handler(poll_answer: PollAnswer):
    poll_id = poll_answer.poll_id
    user_id = poll_owner.get(poll_id)
    if user_id is None:
        return

    session = active_sessions.get(user_id)
    if not session:
        return

    idx = session["index"]
    savol = session["savollar"][idx]
    tanlangan = poll_answer.option_ids[0] if poll_answer.option_ids else None

    if tanlangan == savol["togri"]:
        session["togri_soni"] += 1

    session["index"] += 1
    poll_owner.pop(poll_id, None)
    await keyingi_savol(user_id)


async def testni_yakunla(user_id: int):
    session = active_sessions.pop(user_id, None)
    if not session:
        return

    togri = session["togri_soni"]
    jami = len(session["savollar"])
    foiz = round(togri / jami * 100)

    await bot.send_message(
        user_id,
        f"✅ <b>Test yakunlandi!</b>\n\n"
        f"Fan: {session['subject_nomi']}\n"
        f"Natija: {togri}/{jami} ({foiz}%)\n\n"
        f"Yana yechish uchun guruhda /test buyrug'ini bosing.",
        parse_mode=ParseMode.HTML,
    )

    scores = load_scores()
    user_key = str(user_id)
    entry = scores.setdefault(user_key, {"full_name": session["full_name"], "jami_urinish": 0, "eng_yaxshi_foiz": 0, "fanlar": {}})
    entry["full_name"] = session["full_name"]
    entry["jami_urinish"] += 1
    entry["eng_yaxshi_foiz"] = max(entry["eng_yaxshi_foiz"], foiz)
    entry["fanlar"].setdefault(session["subject_key"], []).append(foiz)
    save_scores(scores)


@dp.message(Command("reyting"))
async def reyting_command(message: Message):
    scores = load_scores()
    if not scores:
        await message.answer("Hozircha hech kim test yechmagan.")
        return

    tartiblangan = sorted(scores.items(), key=lambda x: x[1]["eng_yaxshi_foiz"], reverse=True)[:10]
    matn = "🏆 <b>TOP-10 reyting</b>\n\n"
    for i, (_, d) in enumerate(tartiblangan, 1):
        ism = d.get("full_name", "Noma'lum")
        matn += f"{i}. {ism} — eng yaxshi natija: {d['eng_yaxshi_foiz']}% ({d['jami_urinish']} marta yechgan)\n"

    await message.answer(matn, parse_mode=ParseMode.HTML)


# --- Render'ning "Web Service" turi doim ochiq port kutadi.
# Shu talabni qondirish uchun juda mayda Flask serveri alohida
# oqimda (thread) ishlaydi. UptimeRobot shu manzilga har necha
# daqiqada "salom" deb kirib, botni doim uyg'oq ushlab turadi.
web_app = Flask(__name__)


@web_app.route("/")
def health_check():
    return "Bot ishlayapti!"


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
