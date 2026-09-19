# Verbo — Multilevel Writing/Speaking platformasi

Django platformasi. O'quvchi email + parol bilan kiradi. Ikki rejim:
- **Mock** — biz bergan Multilevel mavzular; tarif limiti bilan (kredit kerak emas).
- **O'z savolim** — o'quvchi o'z savolini kiritadi; KREDIT bilan tekshiriladi.

Baholash: Claude Opus 5 (bo'lmasa Groq — bepul). Multilevel holistik rubrikasi.

## Kredit tizimi
Tekshiruv narxi: Task 1.1 = 1 kredit, Task 1.2 = 2 kredit, Task 2 = 3 kredit.
1 kredit = 1000 so'm. Paketlar: 10 (10 000), 25 (22 000), 50 (40 000) so'm.
- Yangi o'quvchi 3 ta xush kelibsiz krediti oladi.
- Mock tarifini olsa, ustiga BONUS kredit: Arzon +5, Standart +15, Premium +40.
- Kredit faqat "O'z savolim" uchun sarflanadi; mocklar tarif limiti bilan.

## Tariflar (mock uchun)
| Tarif | Speaking | Writing | Bonus kredit | Narx |
|-------|----------|---------|--------------|------|
| Sinov | 2 | 2 | 0 | 0 |
| Arzon | 15 | 15 | +5 | 50 000 |
| Standart | 30 | 30 | +15 | 90 000 |
| Premium | 60 | 60 | +40 | 150 000 |

## RESULT va PDF
Har tekshiruv "Natijalar" bo'limida saqlanadi. Har natijani ochib, "PDF qilib saqlash"
tugmasi orqali brauzer chop etish oynasidan PDF sifatida saqlanadi. PDF yuqorisida
**LOCHINBEK JO'RABOYEV** brendi va **verbo.uz** havolasi chiroyli joylashadi.


## Kirish oqimi (yangi)
- Introduction sahifasi (`/intro/`) — "Get Started" tugmasi.
- Ro'yxat tanlovi (`/boshlash/`): telefon (SMS) yoki email.
- Telefon SMS: real yuborish uchun SMS provayder (Eskiz.uz) kerak — pullik.
  Hozircha test rejimida kod ekranda ko'rsatiladi (SMS_DEBUG=1). Provayder tayyor
  bo'lgach, accounts/sms.py ichidagi send_sms() ni almashtiring.
- Dizayn: faqat oq fon + fon rasmi (to'q rejim olib tashlandi), chap vertikal menyu.

## AI kaliti
```
ANTHROPIC_API_KEY=sk-ant-...     # Opus 5 (production)
GROQ_API_KEY=gsk_...             # yoki bepul Groq (sinash uchun)
```

## Ishga tushirish
```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo          # namuna mock mavzular
export GROQ_API_KEY=gsk_...         # bugun bepul sinash uchun
python manage.py runserver
```
- Sayt: http://127.0.0.1:8000/  · Panel: /boshqaruv/

## O'qituvchi paneli
- Mock mavzu qo'shish: "Writing mavzulari (mock)".
- Kredit qo'shish (to'lovdan keyin): O'quvchini tanlab, amallardan "Kredit qo'shish: +10/+25/+50".
- Tarif berish: o'quvchi tarifini o'zgartiring — mock limit to'ladi + bonus kredit qo'shiladi.

## Keyingi bosqichlar
- Speaking AI (ovoz + transkripsiya).
- Payme: kredit va tarif to'lovini avtomatlashtirish (YATT/merchant tayyor bo'lgach).
