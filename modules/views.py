"""Verbo — Speaking (placeholder), Writing mock + o'z-savol, RESULT va PDF."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .ai import AIError, TASKS, TASK_CHOICES, score_writing
from .models import WritingResult, WritingTopic
from accounts.tiers import credit_cost, CREDIT_PACKAGES


# ---------------- SPEAKING (placeholder) ----------------
@login_required
def speaking(request):
    return render(request, "modules/speaking.html", {"remaining": request.user.speaking_remaining})


@login_required
def speaking_start(request):
    if request.method != "POST":
        return redirect("speaking")
    if request.user.spend_speaking():
        return render(request, "modules/session.html",
                      {"kind": "Speaking", "remaining": request.user.speaking_remaining})
    messages.info(request, "Speaking limitingiz tugadi. Tarifni yangilang.")
    return redirect("tariffs")


# ---------------- WRITING: asosiy sahifa ----------------
@login_required
def writing(request):
    topics = WritingTopic.objects.filter(is_active=True)
    grouped = []
    for key, cfg in TASKS.items():
        items = [t for t in topics if t.task_type == key]
        if items:
            grouped.append({"key": key, "label": cfg["label"], "topics": items})
    return render(request, "modules/writing.html", {
        "grouped": grouped,
        "remaining": request.user.writing_remaining,
        "credits": request.user.credits,
    })


# ---------------- WRITING: MOCK rejimi (tarif limiti bilan) ----------------
@login_required
def writing_task(request, topic_id):
    topic = get_object_or_404(WritingTopic, pk=topic_id, is_active=True)
    if request.user.writing_remaining <= 0:
        messages.info(request, "Writing limitingiz tugadi. Tarifni yangilang.")
        return redirect("tariffs")
    return render(request, "modules/writing_task.html", {
        "topic": topic, "task": TASKS[topic.task_type],
        "remaining": request.user.writing_remaining,
    })


@login_required
def writing_submit(request, topic_id):
    topic = get_object_or_404(WritingTopic, pk=topic_id, is_active=True)
    if request.method != "POST":
        return redirect("writing_task", topic_id=topic.id)
    if request.user.writing_remaining <= 0:
        messages.info(request, "Writing limitingiz tugadi. Tarifni yangilang.")
        return redirect("tariffs")
    answer = (request.POST.get("answer") or "").strip()
    if len(answer) < 10:
        messages.error(request, "Javob juda qisqa. Iltimos, to'liqroq yozing.")
        return redirect("writing_task", topic_id=topic.id)

    try:
        result = score_writing(topic.task_type, topic.prompt_text, answer)
    except AIError as e:
        messages.error(request, f"Baholab bo'lmadi: {e} Qayta urinib ko'ring.")
        return redirect("writing_task", topic_id=topic.id)

    request.user.spend_writing()   # mock: tarif limiti
    saved = WritingResult.objects.create(
        student=request.user, mode="mock", task_type=topic.task_type,
        title=topic.title, prompt_text=topic.prompt_text, answer_text=answer,
        score=result.get("score"), max_score=result.get("max_score", TASKS[topic.task_type]["max"]),
        level=result.get("level", ""), feedback_json=result, credits_spent=0)
    return redirect("result_detail", result_id=saved.id)


# ---------------- WRITING: O'Z-SAVOL rejimi (kredit bilan) ----------------
@login_required
def writing_own(request):
    tasks = [{"key": k, "label": TASKS[k]["label"], "words": TASKS[k]["words"],
              "cost": credit_cost(k)} for k, _ in TASK_CHOICES]
    return render(request, "modules/writing_own.html", {
        "tasks": tasks, "credits": request.user.credits,
        "recent": request.user.writing_results.all()[:4],
    })


@login_required
def writing_own_submit(request):
    if request.method != "POST":
        return redirect("writing_own")

    task_type = request.POST.get("task_type")
    prompt = (request.POST.get("prompt") or "").strip()
    answer = (request.POST.get("answer") or "").strip()

    if task_type not in TASKS:
        messages.error(request, "Topshiriq turini tanlang.")
        return redirect("writing_own")
    if len(prompt) < 5:
        messages.error(request, "Savol matnini kiriting.")
        return redirect("writing_own")
    if len(answer) < 10:
        messages.error(request, "Javob juda qisqa.")
        return redirect("writing_own")

    cost = credit_cost(task_type)
    if not request.user.can_afford(task_type):
        messages.info(request, f"Kredit yetarli emas ({cost} kerak, sizda {request.user.credits}). "
                               "Kredit sotib oling.")
        return redirect("credits")

    try:
        result = score_writing(task_type, prompt, answer)
    except AIError as e:
        messages.error(request, f"Baholab bo'lmadi: {e} Kreditingiz sarflanmadi.")
        return redirect("writing_own")

    spent = request.user.spend_credits(task_type)   # o'z savoli: kredit
    saved = WritingResult.objects.create(
        student=request.user, mode="own", task_type=task_type,
        title="O'z savolim", prompt_text=prompt, answer_text=answer,
        score=result.get("score"), max_score=result.get("max_score", TASKS[task_type]["max"]),
        level=result.get("level", ""), feedback_json=result, credits_spent=spent)
    return redirect("result_detail", result_id=saved.id)


# ---------------- RESULT bo'limi ----------------
@login_required
def results(request):
    qs = request.user.writing_results.all()
    items = list(qs[:50])
    total = 0.0; n = 0
    for r in items:
        if r.score is not None and r.max_score:
            total += (r.score / r.max_score) * 100; n += 1
    avg = round(total / n) if n else 0
    return render(request, "modules/results.html", {
        "results": items, "avg": avg, "count": len(items)})


@login_required
def result_detail(request, result_id):
    r = get_object_or_404(WritingResult, pk=result_id, student=request.user)
    return render(request, "modules/result_detail.html", {
        "r": r, "fb": r.feedback_json, "task": TASKS.get(r.task_type, {}),
    })


# ---------------- Kredit paketlari ----------------
@login_required
def credits(request):
    return render(request, "modules/credits.html", {
        "packages": CREDIT_PACKAGES, "credits": request.user.credits,
    })


# ---------------- VOCABULARY (dizayn — demo, backend keyin ulanadi) ----------------
# Bu ma'lumot vaqtincha demo. Keyin WritingTopic kabi model bilan almashtiriladi.
VOCAB_CATEGORIES = [
    {"key": "daily", "label": "Daily Life", "icon": "sun", "color": "yellow", "count": 8},
    {"key": "academic", "label": "Academic", "icon": "cap", "color": "blue", "count": 6},
    {"key": "business", "label": "Business", "icon": "bag", "color": "violet", "count": 5},
    {"key": "travel", "label": "Travel", "icon": "plane", "color": "green", "count": 7},
    {"key": "tech", "label": "Technology", "icon": "chip", "color": "pink", "count": 4},
    {"key": "ielts", "label": "IELTS", "icon": "star", "color": "peach", "count": 6},
]
VOCAB_QUIZZES = [
    {"title": "Academic Vocabulary", "desc": "Build your academic word list.", "words": 20, "diff": "Medium", "color": "blue", "icon": "cap"},
    {"title": "Business English", "desc": "Useful words for meetings and everyday work.", "words": 15, "diff": "Easy", "color": "violet", "icon": "bag"},
    {"title": "Travel Vocabulary", "desc": "Be ready for your next trip.", "words": 15, "diff": "Medium", "color": "green", "icon": "plane"},
    {"title": "Technology Words", "desc": "Words for the digital world.", "words": 20, "diff": "Hard", "color": "pink", "icon": "chip"},
]


@login_required
def vocabulary(request):
    return render(request, "modules/vocabulary.html", {
        "categories": VOCAB_CATEGORIES, "quizzes": VOCAB_QUIZZES})
