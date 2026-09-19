"""Verbo — o'qituvchi (boshqaruv) paneli. Faqat is_staff foydalanuvchilar uchun."""
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import User
from modules.models import WritingResult

staff_only = user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url="login")


def _avg_percent(results):
    total, n = 0.0, 0
    for r in results:
        if r.score is not None and r.max_score:
            total += (r.score / r.max_score) * 100
            n += 1
    return round(total / n) if n else 0


@staff_only
def dashboard(request):
    students = User.objects.filter(is_staff=False)
    results = WritingResult.objects.all()
    ctx = {
        "n_students": students.count(),
        "n_results": results.count(),
        "avg": _avg_percent(list(results.only("score", "max_score"))),
        "n_credits": sum(u.credits for u in students),
        "recent_students": students.order_by("-date_joined")[:6],
        "recent_results": results.select_related("student")[:8],
    }
    return render(request, "panel/dashboard.html", ctx)


@staff_only
def students(request):
    q = (request.GET.get("q") or "").strip()
    qs = User.objects.filter(is_staff=False)
    if q:
        qs = qs.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(phone__icontains=q))
    return render(request, "panel/students.html", {"students": qs.order_by("-date_joined"), "q": q})


@staff_only
def student_detail(request, uid):
    s = get_object_or_404(User, pk=uid)
    results = list(s.writing_results.all()[:80])
    return render(request, "panel/student_detail.html", {
        "s": s, "results": results, "avg": _avg_percent(results), "count": len(results)})


@staff_only
def all_results(request):
    results = WritingResult.objects.select_related("student")[:120]
    return render(request, "panel/results.html", {"results": results})
