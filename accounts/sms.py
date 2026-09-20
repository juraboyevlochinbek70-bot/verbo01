"""Verbo — SMS yuborish (Eskiz.uz).

Ikki rejim:
  1) TEST rejimi (default) — Eskiz kredensiallari kiritilmagan bo'lsa,
     kod konsolga yoziladi va ekranda ko'rsatiladi. Pul ketmaydi, YaTT shart emas.
  2) REAL rejimi — ESKIZ_EMAIL va ESKIZ_PASSWORD muhit o'zgaruvchilari bo'lsa,
     Eskiz.uz orqali haqiqiy SMS yuboriladi.

Muhit o'zgaruvchilari (Render → Environment):
  ESKIZ_EMAIL     — Eskiz.uz hisobingiz emaili
  ESKIZ_PASSWORD  — Eskiz.uz paroli
  ESKIZ_FROM      — jo'natuvchi nomi (default "4546" = Eskiz test raqami)
  SMS_DEBUG       — "1" bo'lsa kodni ekranda ham ko'rsatadi (test uchun)
"""
import os
import random
import time
import logging

import requests

log = logging.getLogger("verbo.sms")

ESKIZ_EMAIL = os.environ.get("ESKIZ_EMAIL", "").strip()
ESKIZ_PASSWORD = os.environ.get("ESKIZ_PASSWORD", "").strip()
ESKIZ_FROM = os.environ.get("ESKIZ_FROM", "4546").strip()

# Eskiz kredensiallari bo'lsa — real SMS yoqilgan
ESKIZ_ENABLED = bool(ESKIZ_EMAIL and ESKIZ_PASSWORD)

# Kodni ekranda ko'rsatamizmi? Real SMS yoqilmagan bo'lsa — default True.
SMS_DEBUG = os.environ.get("SMS_DEBUG", "0" if ESKIZ_ENABLED else "1") == "1"

_BASE = "https://notify.eskiz.uz/api"
_token = {"value": None, "ts": 0}
_TOKEN_TTL = 60 * 60 * 24 * 20  # ~20 kun (Eskiz tokeni ~30 kun yashaydi)


def generate_code():
    return f"{random.randint(100000, 999999)}"


def _norm_phone(phone):
    """Faqat raqamlar: +998 90 123 45 67 -> 998901234567."""
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) == 9:            # 901234567 -> 998901234567
        digits = "998" + digits
    return digits


def _get_token(force=False):
    """Eskiz tokenini oladi (keshlaydi)."""
    now = time.time()
    if not force and _token["value"] and (now - _token["ts"]) < _TOKEN_TTL:
        return _token["value"]
    resp = requests.post(
        f"{_BASE}/auth/login",
        data={"email": ESKIZ_EMAIL, "password": ESKIZ_PASSWORD},
        timeout=15,
    )
    resp.raise_for_status()
    token = resp.json().get("data", {}).get("token")
    if not token:
        raise RuntimeError(f"Eskiz token olinmadi: {resp.text[:200]}")
    _token["value"] = token
    _token["ts"] = now
    return token


def _eskiz_send(phone, text):
    """Eskiz orqali bitta SMS yuboradi. Muvaffaqiyatda True."""
    mobile = _norm_phone(phone)
    for attempt in (1, 2):  # 401 bo'lsa tokenni yangilab bir marta qayta uriladi
        token = _get_token(force=(attempt == 2))
        resp = requests.post(
            f"{_BASE}/message/sms/send",
            headers={"Authorization": f"Bearer {token}"},
            data={"mobile_phone": mobile, "message": text, "from": ESKIZ_FROM},
            timeout=15,
        )
        if resp.status_code == 401 and attempt == 1:
            continue  # token eskirgan — yangilaymiz
        if resp.status_code in (200, 201):
            return True
        log.warning("Eskiz SMS xato (%s): %s", resp.status_code, resp.text[:300])
        return False
    return False


def send_sms(phone, text):
    """Rejimga qarab SMS yuboradi. Xato bo'lsa ham ilova ishlashda davom etadi."""
    if not ESKIZ_ENABLED:
        # TEST rejimi — kod konsolga chiqadi, ekranda ham ko'rsatiladi (SMS_DEBUG).
        print(f"[SMS(test) -> {phone}] {text}")
        return True
    try:
        ok = _eskiz_send(phone, text)
        if not ok:
            print(f"[SMS(fail) -> {phone}] {text}")
        return ok
    except Exception as e:  # tarmoq/kredensial xatosi — ilova to'xtamasin
        log.exception("Eskiz SMS yuborishda xato: %s", e)
        print(f"[SMS(error) -> {phone}] {text}")
        return False
