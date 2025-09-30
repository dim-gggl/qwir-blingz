from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.middleware.csrf import get_token
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import LoginForm, RegistrationForm
from .services import (
    build_feed_carousels,
    build_theme_detail,
    fetch_random_queer_movie,
    get_feed_themes,
)


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


class FeedView(LoginRequiredMixin, TemplateView):
    template_name = "frontend/feed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = getattr(self.request, "LANGUAGE_CODE", None)
        context["feed_themes"] = get_feed_themes()
        context["carousels"] = build_feed_carousels(self.request.user, language=language)
        context["csrf_token"] = get_token(self.request)
        return context


class ThemeDetailView(LoginRequiredMixin, TemplateView):
    template_name = "frontend/theme_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        language = getattr(self.request, "LANGUAGE_CODE", None)
        detail = build_theme_detail(slug, user=self.request.user, language=language)
        if detail is None:
            raise Http404("Thème introuvable")
        context["detail"] = detail
        context["feed_themes"] = get_feed_themes()
        context["csrf_token"] = get_token(self.request)
        return context
