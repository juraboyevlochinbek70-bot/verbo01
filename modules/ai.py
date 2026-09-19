"""
Verbo — Writing baholash dvigateli.

Ikki provayderni qoʻllab-quvvatlaydi:
  1. Anthropic Claude Opus 5  — eng sifatli (ANTHROPIC_API_KEY boʻlsa ishlatiladi)
  2. Groq (Llama 3.3 70B)     — BEPUL, sinash uchun (GROQ_API_KEY boʻlsa)

Anthropic kaliti boʻlsa — doim oʻsha afzal. Boʻlmasa Groq'ga tushadi.
Multilevel imtihonining holistik rubrikasi asosida baholaydi.
"""
import json
import os
import re

import requests

TIMEOUT = 60

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-opus-5"                 # eng sifatli
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"            # bepul, sinash uchun

# --- Multilevel Writing topshiriqlari va maksimal ballari ---
TASKS = {
    "task1_1": {"label": "Task 1.1 — Norasmiy xat (informal e-mail)",
                "words": "~50 soʻz", "target": "B1–B2", "max": 5},
    "task1_2": {"label": "Task 1.2 — Rasmiy xat (formal letter)",
                "words": "120–150 soʻz", "target": "B2", "max": 5},
    "task2":   {"label": "Task 2 — Blogpost / forum / maqola",
                "words": "180–200 soʻz", "target": "C1", "max": 6},
}
TASK_CHOICES = [(k, v["label"]) for k, v in TASKS.items()]


class AIError(Exception):
    """Baholash amalga oshmaganda koʻtariladi (urinish sarflanmaydi)."""


def _rubric(task_key):
    t = TASKS[task_key]
    return (
        f"Bu — Oʻzbekiston Multilevel imtihonining Writing qismidagi "
        f"«{t['label']}» topshirigʻi. Kutilgan hajm: {t['words']}. "
        f"Maqsad daraja: {t['target']}. Baho shkalasi: 0 dan {t['max']} gacha "
        f"(holistik). Mezonlar: topshiriqni bajarish, registr/uslub, grammatika, "
        f"tinish belgilari va imlo, lugʻat boyligi, bogʻlanish (cohesion), hajm. "
        f"Javob juda qisqa yoki mavzuga aloqasiz boʻlsa, ball past boʻlsin."
    )


def _system_prompt(task_key):
    max_score = TASKS[task_key]["max"]
    return (
        "Siz Multilevel ingliz tili imtihoni uchun tajribali Writing ekspertisiz. "
        "Talaba javobini adolatli baholaysiz. Izohlarni OʻZBEK TILIDA yozasiz, "
        "xato va tuzatishlarni ingliz tilida koʻrsatasiz.\n\n"
        f"{_rubric(task_key)}\n\n"
        "Javobni FAQAT quyidagi JSON koʻrinishida qaytaring (boshqa matn yoki ``` yoʻq):\n"
        "{\n"
        f'  "score": <0..{max_score}>,\n'
        f'  "max_score": {max_score},\n'
        '  "level": "<A2|B1|B2|C1>",\n'
        '  "summary": "<2-3 gap xulosa, oʻzbekcha>",\n'
        '  "strengths": ["<kuchli tomon, oʻzbekcha>", ...],\n'
        '  "errors": [{"type":"<grammar|vocabulary|spelling|register|cohesion>",'
        '"original":"<inglizcha>","correction":"<inglizcha>","note":"<oʻzbekcha izoh>"}, ...],\n'
        '  "advice": "<2-3 amaliy maslahat, oʻzbekcha>"\n'
        "}"
    )


def score_writing(task_key, prompt_text, answer_text):
    """Javobni baholaydi (dict qaytaradi). Xatolikda AIError."""
    if task_key not in TASKS:
        raise AIError("Notoʻgʻri topshiriq turi.")

    system = _system_prompt(task_key)
    user_msg = (
        f"TOPSHIRIQ (savol):\n{prompt_text}\n\n"
        f"TALABA JAVOBI:\n{answer_text}\n\n"
        "Yuqoridagi javobni baholang va faqat JSON qaytaring."
    )

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()

    if anthropic_key:
        text = _call_anthropic(anthropic_key, system, user_msg, TASKS[task_key]["max"])
    elif groq_key:
        text = _call_groq(groq_key, system, user_msg)
    else:
        raise AIError("AI kaliti ulanmagan (ANTHROPIC_API_KEY yoki GROQ_API_KEY kerak).")

    try:
        parsed = _extract_json(text)
    except ValueError as e:
        raise AIError(f"AI javobini oʻqib boʻlmadi: {e}")

    parsed.setdefault("max_score", TASKS[task_key]["max"])
    parsed.setdefault("errors", [])
    parsed.setdefault("strengths", [])
    return parsed


def _call_anthropic(key, system, user_msg, max_score):
    payload = {
        "model": ANTHROPIC_MODEL, "max_tokens": 1500, "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01",
               "content-type": "application/json"}
    try:
        r = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AIError(f"Anthropic'ga ulanib boʻlmadi: {e}")
    if r.status_code != 200:
        raise AIError(f"Anthropic xatosi (kod {r.status_code}). Balansni tekshiring.")
    data = r.json()
    return "".join(b.get("text", "") for b in data.get("content", [])
                   if b.get("type") == "text")


def _call_groq(key, system, user_msg):
    payload = {
        "model": GROQ_MODEL, "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user_msg}],
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AIError(f"Groq'ga ulanib boʻlmadi: {e}")
    if r.status_code != 200:
        raise AIError(f"Groq xatosi (kod {r.status_code}).")
    return r.json()["choices"][0]["message"]["content"]


def _extract_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("JSON topilmadi")
    return json.loads(text[start:end + 1])
