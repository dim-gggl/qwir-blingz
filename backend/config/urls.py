"""URL configuration for Qwir Blingz."""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from planets.api import PlanetBuilderViewSet
from media_catalog.api import IdentityTagViewSet, MediaListViewSet

router = DefaultRouter()
router.register(r"planets", PlanetBuilderViewSet, basename="planet-builder")
router.register(r"media-lists", MediaListViewSet, basename="media-list")
router.register(r"identity-tags", IdentityTagViewSet, basename="identity-tag")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("frontend.urls")),
    path("api/", include(router.urls)),
]
