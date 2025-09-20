from __future__ import annotations

from django.apps import AppConfig


class MediaCatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "media_catalog"
    verbose_name = "Media Catalog"
