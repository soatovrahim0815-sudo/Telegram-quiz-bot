# Telegram Test Bot — o'rnatish qo'llanmasi

Bu bot guruhda `/test` deyilganda fanlar ro'yxatini chiqaradi, kimdir fanni tanlasa,
uni shaxsiy chatga o'tkazib, avtomatik test tashlaydi (Telegramning quiz-poll
formatida), natijani hisoblab, `/reyting` orqali TOP-10 ni ko'rsatadi.

Kod yozish bilimi shart emas — quyidagi qadamlarni ketma-ket bajaring.

---

## 1-qadam: Python o'rnatish

1. https://www.python.org/downloads/ saytiga kiring
2. "Download Python 3.12" (yoki eng yangi versiya) tugmasini bosing
3. O'rnatishda **"Add Python to PATH"** katakchasini albatta belgilang
4. O'rnatib bo'lgach, kompyuteringizda terminal (Windows'da "Command Prompt" yoki
   "PowerShell", Mac'da "Terminal") oching va tekshiring:
   ```
   python --version
   ```
   Versiya raqami chiqsa — hammasi joyida.

## 2-qadam: Botni @BotFather orqali yaratish

1. Telegram'da **@BotFather** ni toping va `/start` bosing
2. `/newbot` buyrug'ini yuboring
3. Botingizga nom bering (masalan: "DTM Test Praktikum")
4. Username bering — oxiri albatta `bot` bilan tugashi kerak
   (masalan: `dtm_test_praktikum_bot`)
5. BotFather sizga **token** beradi — bu maxfiy raqam-harf ketma-ketligi, uni
   hech kimga bermang, saqlab qo'ying

## 3-qadam: Fayllarni joylashtirish

1. Kompyuteringizda yangi papka yarating, masalan: `telegram-test-bot`
2. Ushbu suhbatdan yuklab olingan barcha fayllarni (`bot.py`, `config.py`,
   `questions.json`, `requirements.txt`) shu papkaga joylashtiring

## 4-qadam: config.py faylini to'ldirish

`config.py` faylini istalgan matn muharriri bilan oching (Notepad ham bo'laveradi)
va quyidagilarni almashtiring:

```python
BOT_TOKEN = "BU_YERGA_TOKENINGIZNI_QOYING"        # 2-qadamda olgan tokeningiz
BOT_USERNAME = "BOT_USERNAMEINGIZNI_QOYING"       # @ belgisisiz, masalan: dtm_test_praktikum_bot
```

Saqlang.

## 5-qadam: Kerakli kutubxonani o'rnatish

Terminalni oching, `cd` buyrug'i bilan papkangizga o'ting, masalan:
```
cd Desktop/telegram-test-bot
```
So'ng:
```
pip install -r requirements.txt
```

## 6-qadam: Botni ishga tushirish

```
python bot.py
```

Agar terminalda "Bot ishga tushdi..." degan yozuv chiqsa — bot ishlayapti!
(Terminalni yopsangiz, bot ham to'xtaydi — buni pastdagi "Botni doim ishlab
turishi" bo'limida qanday hal qilish yozilgan.)

## 7-qadam: Botni guruhga qo'shish

1. Test o'tkazmoqchi bo'lgan guruhingizni oching
2. "Add member" orqali botingizni qo'shing (username orqali qidiring)
3. Guruhda kimdir `/test` deb yozsin — bot fanlar ro'yxatini chiqaradi
4. Fanni bosgach, u odam botning shaxsiy chatiga o'tkaziladi va test
   avtomatik boshlanadi

**Muhim:** foydalanuvchi tugmani bosganda birinchi marta botning shaxsiy
chatini ochishi kerak bo'ladi (Telegram o'zi ochib beradi) — bu normal holat.

---

## Reyting ko'rish

Guruhda `/reyting` deb yozing — eng yaxshi 10 ta natija chiqadi.
Natijalar `scores.json` faylida avtomatik saqlanadi.

## Yangi fan qo'shish

`questions.json` faylini oching, mavjud `"ona_tili"` blokiga o'xshab yangi
fan qo'shing:

```json
"matematika": {
  "nomi": "Matematika",
  "savollar": [
    {
      "mavzu": "Algebra",
      "savol": "2 + 2 x 2 nechaga teng?",
      "variantlar": ["6", "8", "4", "2"],
      "togri": 0
    }
  ]
}
```
`"togri"` — to'g'ri javobning tartib raqami, lekin 0 dan boshlanadi
(0 = birinchi variant, 1 = ikkinchi, va hokazo).

Har bir fan bo'yicha savollarni menga aytsangiz, men shu formatda tayyorlab
beraman — shunchaki faylga qo'shib qo'yasiz, kodga tegishning hojati yo'q.

## Botni doim ishlab turishi (keyingi qadam)

Hozirgi holatda bot faqat kompyuteringiz yoqiq va terminal ochiq turgandagina
ishlaydi. Botni 24/7 ishlatish uchun keyinchalik arzon serverga (VPS) joylash
kerak bo'ladi (masalan Timeweb, Hostinger, yoki Railway.app kabi xizmatlar).
Bot ishlay boshlagach va uni sinab ko'rgach, shu bosqichda ham yordam bera
olaman.
