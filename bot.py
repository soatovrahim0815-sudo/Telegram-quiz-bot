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


async def main():
    # Flask serverini alohida oqimda (thread) ishga tushiramiz
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Bot va Flask server ishga tushdi...")
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
