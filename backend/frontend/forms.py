from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 bg-white/80 px-3 py-2 text-slate-900 shadow-sm focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500",
                "placeholder": "Username",
            }
        ),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 bg-white/80 px-3 py-2 text-slate-900 shadow-sm focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500",
                "placeholder": "Password",
            }
        ),
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 bg-white/80 px-3 py-2 text-slate-900 shadow-sm focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500",
                "placeholder": "Email (optional)",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full rounded-md border border-slate-300 bg-white/80 px-3 py-2 text-slate-900 shadow-sm focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500",
                    "placeholder": "Username",
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field_name in ("password1", "password2"):
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "w-full rounded-md border border-slate-300 bg-white/80 px-3 py-2 text-slate-900 shadow-sm focus:border-fuchsia-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500",
                }
            )
            self.fields[field_name].help_text = ""
