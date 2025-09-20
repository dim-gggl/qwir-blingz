from __future__ import annotations

from django.urls import path

from .api import QueerFilmTeaserView
from .views import WelcomeView

app_name = "frontend"

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),
    path("api/teasers/queer-film/", QueerFilmTeaserView.as_view(), name="queer-film-teaser"),
]
