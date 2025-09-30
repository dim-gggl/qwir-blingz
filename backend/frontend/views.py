from __future__ import annotations

from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import LoginForm, RegistrationForm
from .services import fetch_random_queer_movie


class WelcomeView(TemplateView):
    template_name = "frontend/welcome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_form"] = LoginForm(self.request)
        context["registration_form"] = RegistrationForm()
        context["random_movie"] = fetch_random_queer_movie()
        context["login_url"] = reverse_lazy("login")
        context["signup_url"] = reverse_lazy("signup") if self._signup_url_exists() else reverse_lazy("login")
        return context

    def _signup_url_exists(self) -> bool:
        from django.urls import resolve, Resolver404

        try:
            resolve("/signup/")
        except Resolver404:
            return False
        return True


class SignupView(FormView):
    template_name = "frontend/welcome.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("frontend:feed")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_form"] = LoginForm(self.request)
        context["registration_form"] = context["form"]
        context["random_movie"] = fetch_random_queer_movie()
        context["login_url"] = reverse_lazy("login")
        context["signup_url"] = reverse_lazy("frontend:signup")
        return context


class FeedView(TemplateView):
    template_name = "frontend/feed.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("frontend:welcome")
        return super().dispatch(request, *args, **kwargs)
