"""Verbo modullari — Writing mavzulari (mock) va saqlangan natijalar."""
from django.conf import settings
from django.db import models

from .ai import TASK_CHOICES


class WritingTopic(models.Model):
    """O'qituvchi qo'shadigan MOCK Writing mavzusi (topshiriq matni)."""
    task_type = models.CharField("Topshiriq turi", max_length=20, choices=TASK_CHOICES)
    title = models.CharField("Sarlavha", max_length=200)
    prompt_text = models.TextField("Topshiriq matni (savol)")
    is_active = models.BooleanField("Faol", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writing mavzusi (mock)"
        verbose_name_plural = "Writing mavzulari (mock)"
        ordering = ["task_type", "title"]

    def __str__(self):
        return f"[{self.get_task_type_display()}] {self.title}"


class WritingResult(models.Model):
    """Har bir tekshiruv natijasi — mock yoki o'z-savol. RESULT bo'limida ko'rinadi."""
    MODE_CHOICES = [("mock", "Mock (bizning mavzu)"), ("own", "O'z savoli")]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="writing_results")
    mode = models.CharField("Rejim", max_length=8, choices=MODE_CHOICES, default="mock")
    task_type = models.CharField("Topshiriq turi", max_length=20, choices=TASK_CHOICES)
    title = models.CharField("Sarlavha", max_length=200, blank=True)
    prompt_text = models.TextField("Savol matni")
    answer_text = models.TextField("Talaba javobi")

    score = models.FloatField("Ball", null=True, blank=True)
    max_score = models.PositiveIntegerField("Maksimal ball", default=5)
    level = models.CharField("Daraja", max_length=10, blank=True)
    feedback_json = models.JSONField("AI izohi", default=dict, blank=True)
    credits_spent = models.PositiveIntegerField("Sarflangan kredit", default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writing natijasi"
        verbose_name_plural = "Writing natijalari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.score}/{self.max_score} ({self.level})"
