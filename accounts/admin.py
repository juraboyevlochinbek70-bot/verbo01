"""Verbo — o'qituvchi boshqaruv paneli."""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm

from .models import User
from .tiers import limits_for, bonus_credits_for


class AddCreditsForm(forms.Form):
    amount = forms.IntegerField(label="Qo'shiladigan kredit", min_value=1, initial=10)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    change_password_form = AdminPasswordChangeForm
    ordering = ["-date_joined"]
    list_display = ("email", "first_name", "tier", "credits",
                    "speaking_remaining", "writing_remaining", "date_joined")
    list_filter = ("tier", "is_active", "is_staff")
    search_fields = ("email", "first_name")
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Ma'lumot", {"fields": ("first_name",)}),
        ("Tarif va mock limiti", {
            "fields": ("tier", "speaking_remaining", "writing_remaining"),
            "description": "Tarifni o'zgartirib saqlasangiz — mock limitlari to'ladi "
                           "va tarifning bonus krediti hamyoniga qo'shiladi.",
        }),
        ("Kredit hamyoni (o'z savollari uchun)", {
            "fields": ("credits",),
            "description": "Kredit paketi to'lovidan keyin shu yerga kredit qo'shing "
                           "yoki pastdagi 'Kredit qo'shish' amalidan foydalaning.",
        }),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Sanalar", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("email", "first_name", "tier", "password1", "password2")}),
    )

    actions = ["grant_tier_benefits", "add_10_credits", "add_25_credits", "add_50_credits"]

    @admin.action(description="Tarif imtiyozlarini berish (mock limit + bonus kredit)")
    def grant_tier_benefits(self, request, queryset):
        for u in queryset:
            u.speaking_remaining, u.writing_remaining = limits_for(u.tier)
            u.credits = u.credits + bonus_credits_for(u.tier)
            u.save(update_fields=["speaking_remaining", "writing_remaining", "credits"])
        self.message_user(request, f"{queryset.count()} ta o'quvchiga imtiyoz berildi.")

    def _add_credits(self, request, queryset, n):
        for u in queryset:
            u.add_credits(n)
        self.message_user(request, f"{queryset.count()} ta o'quvchiga {n} kreditdan qo'shildi.")

    @admin.action(description="Kredit qo'shish: +10 (10,000 so'm paketi)")
    def add_10_credits(self, request, queryset):
        self._add_credits(request, queryset, 10)

    @admin.action(description="Kredit qo'shish: +25 (22,000 so'm paketi)")
    def add_25_credits(self, request, queryset):
        self._add_credits(request, queryset, 25)

    @admin.action(description="Kredit qo'shish: +50 (40,000 so'm paketi)")
    def add_50_credits(self, request, queryset):
        self._add_credits(request, queryset, 50)
