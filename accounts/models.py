"""Verbo — maxsus foydalanuvchi modeli (email login + tarif limitlari + kredit hamyoni)."""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

from .tiers import (TIER_CHOICES, DEFAULT_TIER, WELCOME_CREDITS,
                    limits_for, credit_cost)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email majburiy.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        extra.setdefault("tier", DEFAULT_TIER)
        sp, wr = limits_for(extra["tier"])
        extra.setdefault("speaking_remaining", sp)
        extra.setdefault("writing_remaining", wr)
        extra.setdefault("credits", WELCOME_CREDITS)   # o'z savolini sinash uchun
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser is_staff=True bo'lishi kerak.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser=True bo'lishi kerak.")
        return self._create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Telefon", max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField("Ism", max_length=120, blank=True)

    tier = models.CharField("Tarif", max_length=20, choices=TIER_CHOICES, default=DEFAULT_TIER)
    speaking_remaining = models.PositiveIntegerField("Speaking qoldi", default=2)
    writing_remaining = models.PositiveIntegerField("Writing qoldi", default=2)
    credits = models.PositiveIntegerField("Kredit (o'z savollari uchun)", default=WELCOME_CREDITS)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = "O'quvchi"
        verbose_name_plural = "O'quvchilar"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.first_name or self.email} ({self.get_tier_display()})"

    # --- Mock tarif / limit ---
    def apply_tier(self, tier_key):
        self.tier = tier_key
        self.speaking_remaining, self.writing_remaining = limits_for(tier_key)

    def can_use_speaking(self):
        return self.speaking_remaining > 0

    def can_use_writing(self):
        return self.writing_remaining > 0

    def spend_speaking(self):
        if self.speaking_remaining > 0:
            self.speaking_remaining -= 1
            self.save(update_fields=["speaking_remaining"])
            return True
        return False

    def spend_writing(self):
        if self.writing_remaining > 0:
            self.writing_remaining -= 1
            self.save(update_fields=["writing_remaining"])
            return True
        return False

    # --- Kredit hamyoni (o'z savollari uchun) ---
    def credit_cost(self, task_key):
        return credit_cost(task_key)

    def can_afford(self, task_key):
        return self.credits >= credit_cost(task_key)

    def spend_credits(self, task_key):
        cost = credit_cost(task_key)
        if self.credits >= cost:
            self.credits -= cost
            self.save(update_fields=["credits"])
            return cost
        return 0

    def add_credits(self, amount):
        self.credits = self.credits + int(amount)
        self.save(update_fields=["credits"])
