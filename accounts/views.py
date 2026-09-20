"""Verbo — kirish sahifalari: intro, ro'yxat tanlovi, email va telefon ro'yxati."""
import re

from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignupForm
from .models import User
from .sms import generate_code, send_sms, SMS_DEBUG, ESKIZ_ENABLED
from .tiers import public_tiers

EMAIL_BACKEND = "django.contrib.auth.backends.ModelBackend"
PHONE_BACKEND = "accounts.auth_backends.PhoneBackend"

# Ro'yxatdan o'tish: DJANGO_REGISTRATION_OPEN=1 bo'lsa yoqiladi.
import os
REGISTRATION_OPEN = os.environ.get("DJANGO_REGISTRATION_OPEN", "0") == "1"

# Telefon/SMS orqali ro'yxat — faqat Eskiz ulangan bo'lsa yoqiladi (aks holda kod
# ekranda ko'rinib qolmasligi uchun yashiriladi). DJANGO_PHONE_REGISTRATION bilan majburan boshqarish mumkin.
PHONE_REGISTRATION = os.environ.get(
    "DJANGO_PHONE_REGISTRATION", "1" if ESKIZ_ENABLED else "0") == "1"


def home(request):
    if not request.user.is_authenticated:
        return redirect("intro")
    return render(request, "home.html", {
        "writing_done": request.user.writing_results.count()})


def intro(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "intro.html")


def register_choice(request):
    """Bitta sahifa: Telefon/Email almashtirgichli ro'yxat."""
    if request.user.is_authenticated:
        return redirect("home")
    if PHONE_REGISTRATION:
        active = "email" if request.GET.get("m") == "email" else "phone"
    else:
        active = "email"
    return render(request, "register.html", {
        "form": SignupForm(), "active": active, "registration_open": REGISTRATION_OPEN,
        "phone_enabled": PHONE_REGISTRATION,
    })


def demo_login(request):
    """Dizaynni ko'rish uchun demo akkaunt bilan kirish (ro'yxatsiz)."""
    from django.utils.crypto import get_random_string
    from modules.models import WritingTopic, WritingResult

    user, created = User.objects.get_or_create(
        email="demo@verbo.local", defaults={"first_name": "Demo"})
    if created:
        user.set_password(get_random_string(16))
    user.tier = "standart"
    user.speaking_remaining = 30
    user.writing_remaining = 30
    user.save()
    # kredit balansini toza 15 qilamiz (tarif signali ta'sir qilmasligi uchun alohida saqlash)
    user.credits = 15
    user.save(update_fields=["credits"])

    # namuna mock mavzular
    if not WritingTopic.objects.exists():
        WritingTopic.objects.create(task_type="task1_1", title="Meeting a friend",
            prompt_text="Your friend is coming to your city. Write a short e-mail (about 50 words).")
        WritingTopic.objects.create(task_type="task1_2", title="Complaint about an online order",
            prompt_text="Write a formal letter (120-150 words) of complaint about a damaged product.")
        WritingTopic.objects.create(task_type="task2", title="Social media and young people",
            prompt_text="Write a blog post (180-200 words). Do you agree social media harms young people?")

    # namuna natija (Natija/PDF sahifasi bo'sh ko'rinmasligi uchun)
    if not WritingResult.objects.filter(student=user).exists():
        WritingResult.objects.create(
            student=user, mode="own", task_type="task1_2", title="O'z savolim",
            prompt_text="Write a formal letter of complaint about a delayed delivery.",
            answer_text="Dear Sir or Madam, I am writing to complain about the delay of my order "
                        "which I has placed two weeks ago. Unfortunately, it has not arrived yet.",
            score=4, max_score=5, level="B2", credits_spent=2,
            feedback_json={
                "score": 4, "max_score": 5, "level": "B2",
                "summary": "Javobingiz rasmiy uslubda va aniq yozilgan. Bir necha grammatik xato bor.",
                "strengths": ["Rasmiy registr to'g'ri tanlangan", "Xatning tuzilishi aniq"],
                "errors": [{"type": "grammar", "original": "I has placed", "correction": "I placed",
                            "note": "O'tgan zamon uchun 'placed' yetarli."}],
                "advice": "Ko'proq bog'lovchi so'zlar (however, therefore) ishlating.",
            })

    login(request, user, backend=EMAIL_BACKEND)
    return redirect("home")


def signup(request):
    """Email orqali ro'yxatdan o'tish (register.html ichidagi Email paneli)."""
    if request.user.is_authenticated:
        return redirect("home")
    if not REGISTRATION_OPEN:
        return redirect("register_choice")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend=EMAIL_BACKEND)
            return redirect("home")
        # Xato bo'lsa — o'sha sahifani Email paneli ochiq holda qayta ko'rsatamiz
        return render(request, "register.html", {
            "form": form, "active": "email", "registration_open": REGISTRATION_OPEN})
    return redirect("register_choice")


def _norm_phone(raw):
    digits = re.sub(r"\D", "", raw or "")
    return "+" + digits if digits else ""


def phone_register(request):
    """Telefon orqali ro'yxat — 1-qadam: raqam va parol."""
    if request.user.is_authenticated:
        return redirect("home")
    if not (REGISTRATION_OPEN and PHONE_REGISTRATION):
        return redirect("register_choice")
    if request.method != "POST":
        return redirect("register_choice")

    phone = _norm_phone(request.POST.get("phone"))
    name = (request.POST.get("first_name") or "").strip()
    pw = request.POST.get("password") or ""
    error = None
    if len(re.sub(r"\D", "", phone)) < 9:
        error = "Telefon raqamini to'g'ri kiriting (masalan +998901234567)."
    elif len(pw) < 6:
        error = "Parol kamida 6 belgidan iborat bo'lsin."
    elif User.objects.filter(phone=phone).exists():
        error = "Bu raqam allaqachon ro'yxatdan o'tgan."
    else:
        code = generate_code()
        request.session["pending_phone"] = {"phone": phone, "name": name, "pw": pw, "code": code}
        send_sms(phone, f"Verbo tasdiqlash kodi: {code}")
        return redirect("phone_verify")

    # Xato — Telefon paneli ochiq holda, kiritilganlarni saqlab qayta ko'rsatamiz
    return render(request, "register.html", {
        "form": SignupForm(), "active": "phone", "error": error,
        "phone": request.POST.get("phone"), "name": name,
    })


def phone_verify(request):
    """Telefon orqali ro'yxat — 2-qadam: SMS kodini tasdiqlash."""
    if request.user.is_authenticated:
        return redirect("home")
    if not (REGISTRATION_OPEN and PHONE_REGISTRATION):
        return redirect("register_choice")
    pending = request.session.get("pending_phone")
    if not pending:
        return redirect("phone_register")

    error = None
    if request.method == "POST":
        entered = (request.POST.get("code") or "").strip()
        if entered == pending["code"]:
            digits = re.sub(r"\D", "", pending["phone"])
            user = User.objects.create_user(
                email=f"{digits}@phone.verbo.local",
                password=pending["pw"],
                first_name=pending["name"],
                phone=pending["phone"],
            )
            del request.session["pending_phone"]
            login(request, user, backend=PHONE_BACKEND)
            return redirect("home")
        error = "Kod noto'g'ri. Qayta urinib ko'ring."

    return render(request, "registration/phone_verify.html", {
        "phone": pending["phone"], "error": error,
        # Real SMS ulanmagan bo'lsa, test uchun kodni ko'rsatamiz:
        "debug_code": pending["code"] if SMS_DEBUG else None,
    })


def tariffs(request):
    return render(request, "tariffs.html", {"tiers": public_tiers()})
