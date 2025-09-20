from __future__ import annotations

from typing import Optional

from django.conf import settings

from .client import TmdbClient


def get_tmdb_client() -> Optional[TmdbClient]:
    config = getattr(settings, "TMDB_CONFIG", {})
    api_key = config.get("API_KEY")
    if not api_key:
        raise ValueError("TMDb API key is not configured")
    return TmdbClient(
        api_key=api_key,
        default_language=config.get("LANGUAGE", "en-US"),
        timeout=float(config.get("TIMEOUT", 10)),
    )
