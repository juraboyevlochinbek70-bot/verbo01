"""O'qituvchi panelda tarif o'zgartirilsa — mock limitlari to'ladi va bonus kredit qo'shiladi."""
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User
from .tiers import limits_for, bonus_credits_for


@receiver(pre_save, sender=User)
def apply_tier_benefits_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    if old.tier != instance.tier:
        # Mock limitlari to'ladi
        instance.speaking_remaining, instance.writing_remaining = limits_for(instance.tier)
        # Bonus kredit QO'SHILADI (o'z savollari uchun) — mavjud kreditni yo'qotmaymiz
        instance.credits = old.credits + bonus_credits_for(instance.tier)
