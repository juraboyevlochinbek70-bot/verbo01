"""Verbo modullari — o'qituvchi paneli: mock mavzular va natijalar."""
from django.contrib import admin
from .models import WritingResult, WritingTopic


@admin.register(WritingTopic)
class WritingTopicAdmin(admin.ModelAdmin):
    list_display = ("title", "task_type", "is_active", "created_at")
    list_filter = ("task_type", "is_active")
    search_fields = ("title", "prompt_text")
    list_editable = ("is_active",)


@admin.register(WritingResult)
class WritingResultAdmin(admin.ModelAdmin):
    list_display = ("student", "mode", "task_type", "score", "max_score",
                    "level", "credits_spent", "created_at")
    list_filter = ("mode", "level", "task_type", "created_at")
    search_fields = ("student__email", "student__first_name", "prompt_text")
    readonly_fields = [f.name for f in WritingResult._meta.fields]

    def has_add_permission(self, request):
        return False
