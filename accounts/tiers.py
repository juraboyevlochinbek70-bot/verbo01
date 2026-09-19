"""
Verbo tariflari va kredit tizimi — bitta joyda.

- Mock tariflari (Arzon/Standart/Premium): bizning mocklarni yechish uchun limit beradi
  va ustiga BONUS KREDIT qo'shadi (o'quvchining o'z savollari uchun).
- Kredit: o'quvchi o'z savolini tekshirtirganda sarflanadi. Alohida paket bilan sotib olinadi.
"""

# --- Har bir topshiriqni tekshirish narxi (kreditda) ---
CREDIT_COST = {
    "task1_1": 1,
    "task1_2": 2,
    "task2": 3,
}

# --- Yangi o'quvchiga xush kelibsiz krediti (o'z savolini bir marta sinash uchun) ---
WELCOME_CREDITS = 3

# --- Kredit paketlari (o'z savollari uchun, alohida sotib olinadi) ---
CREDIT_PACKAGES = [
    {"key": "starter", "name": "Starter", "credits": 50, "price": 19_000, "tag": "",
     "desc": "Perfect for getting into a steady practice rhythm.", "color": "blue"},
    {"key": "practice", "name": "Practice", "credits": 120, "price": 39_000, "tag": "Most popular",
     "desc": "More practice for learners who like to keep going.", "color": "violet"},
    {"key": "pro", "name": "Pro", "credits": 250, "price": 69_000, "tag": "",
     "desc": "For serious learners and bigger goals.", "color": "peach"},
]

TIERS = {
    "trial": {
        "label": "Bepul sinov", "speaking": 2, "writing": 2, "price": 0,
        "bonus_credits": 0, "order": 0, "public": False,
    },
    "arzon": {
        "label": "Arzon", "speaking": 15, "writing": 15, "price": 50_000,
        "bonus_credits": 5, "order": 1, "public": True,
    },
    "standart": {
        "label": "Standart", "speaking": 30, "writing": 30, "price": 90_000,
        "bonus_credits": 15, "order": 2, "public": True,
    },
    "premium": {
        "label": "Premium", "speaking": 60, "writing": 60, "price": 150_000,
        "bonus_credits": 40, "order": 3, "public": True,
    },
}

TIER_CHOICES = [(key, cfg["label"]) for key, cfg in TIERS.items()]
DEFAULT_TIER = "trial"


def limits_for(tier_key):
    cfg = TIERS.get(tier_key, TIERS[DEFAULT_TIER])
    return cfg["speaking"], cfg["writing"]


def bonus_credits_for(tier_key):
    return TIERS.get(tier_key, TIERS[DEFAULT_TIER]).get("bonus_credits", 0)


def credit_cost(task_key):
    return CREDIT_COST.get(task_key, 1)


def public_tiers():
    items = [{"key": k, **v} for k, v in TIERS.items() if v.get("public")]
    return sorted(items, key=lambda x: x["order"])
