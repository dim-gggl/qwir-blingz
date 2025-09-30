from __future__ import annotations

from django.urls import path

from .api import QueerFilmTeaserView
from .views import FeedView, SignupView, WelcomeView

app_name = "frontend"

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("feed/", FeedView.as_view(), name="feed"),
    path("api/teasers/queer-film/", QueerFilmTeaserView.as_view(), name="queer-film-teaser"),
]
