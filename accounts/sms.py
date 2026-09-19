"""Verbo — SMS yuborish (hozircha STUB).

Real SMS uchun O'zbekistonda provayder kerak (masalan Eskiz.uz, Play Mobile) —
bu pullik va alohida akkaunt/API talab qiladi. Hozircha kod ekranda ko'rsatiladi
(test rejimi). Provayder tayyor bo'lgach, shu funksiya ichini almashtiramiz.
"""
import os
import random


def generate_code():
    return f"{random.randint(100000, 999999)}"


def send_sms(phone, text):
    """Hozircha faqat konsolga yozadi. Real SMS uchun Eskiz.uz ulanadi."""
    print(f"[SMS -> {phone}] {text}")
    return True


# Test rejimida kodni ekranda ko'rsatamizmi? (real SMS ulanmagan bo'lsa True)
SMS_DEBUG = os.environ.get("SMS_DEBUG", "1") == "1"
