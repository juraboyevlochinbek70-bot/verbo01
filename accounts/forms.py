"""Verbo — roʻyxatdan oʻtish formasi (email + ism + parol)."""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "email@misol.com"}),
    )
    first_name = forms.CharField(
        label="Ism",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Ismingiz"}),
    )

    class Meta:
        model = User
        fields = ("email", "first_name")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon roʻyxatdan oʻtgan.")
        return email
