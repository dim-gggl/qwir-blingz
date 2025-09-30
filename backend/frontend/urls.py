from django.urls import path

from .api import FeedCarouselRefreshView, QueerFilmTeaserView
from .views import FeedView, ThemeDetailView, WelcomeView

app_name = "frontend"

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),
    path("feed/", FeedView.as_view(), name="feed"),
    path("feed/themes/<slug:slug>/", ThemeDetailView.as_view(), name="theme-detail"),
    path("api/teasers/queer-film/", QueerFilmTeaserView.as_view(), name="queer-film-teaser"),
    path(
        "api/feed/carousels/<slug:slug>/",
        FeedCarouselRefreshView.as_view(),
        name="feed-carousel-refresh",
    ),
]
