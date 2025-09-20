"""URL configuration for Qwir Blingz."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from planets.api import PlanetBuilderViewSet

router = DefaultRouter()
router.register(r"planets", PlanetBuilderViewSet, basename="planet-builder")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("frontend.urls")),
    path("api/", include(router.urls)),
]
