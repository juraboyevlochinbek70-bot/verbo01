"""Sinash uchun namuna Writing mavzularini qoʻshadi.

Ishlatish:  python manage.py seed_demo
Bu mavzular NAMUNA — keyin paneldan oʻchirib, oʻzingiznikini qoʻshasiz.
"""
from django.core.management.base import BaseCommand

from modules.models import WritingTopic

SAMPLES = [
    ("task1_1", "Meeting a friend",
     "Your friend Alex is coming to your city next week. Write a short e-mail (about 50 words): "
     "thank Alex for the message, suggest a place to meet, and say what time is good for you."),
    ("task1_2", "Complaint about an online order",
     "You bought a jacket from an online shop, but it arrived damaged and in the wrong size. "
     "Write a formal letter (120–150 words) to the customer service: explain the problem, "
     "say how it affected you, and request a solution."),
    ("task2", "Social media and young people",
     "Write a blog post (180–200 words). Some people think social media does more harm than good "
     "for young people. Do you agree or disagree? Give your opinion with reasons and examples."),
]


class Command(BaseCommand):
    help = "Namuna Writing mavzularini qoʻshadi (sinash uchun)."

    def handle(self, *args, **options):
        created = 0
        for task_type, title, prompt in SAMPLES:
            obj, made = WritingTopic.objects.get_or_create(
                title=title, defaults={"task_type": task_type, "prompt_text": prompt})
            if made:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {created} ta namuna mavzu qoʻshildi. "
            f"Ularni /boshqaruv/ da tahrirlashingiz yoki oʻchirishingiz mumkin."))
