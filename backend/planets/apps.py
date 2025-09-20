from __future__ import annotations

from django.apps import AppConfig


class PlanetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "planets"
    verbose_name = "Community Planets"
