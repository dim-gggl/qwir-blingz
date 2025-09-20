"""Celery task stubs for planet generation."""

from __future__ import annotations

import logging
from typing import Optional

LOGGER = logging.getLogger(__name__)


def enqueue_planet_generation(*, planet_id: int, appearance_id: Optional[int] = None) -> None:
    """Placeholder hook for the planet art generation pipeline.

    This function will later delegate to Celery or another background worker to
    render the hero and icon imagery. For now we simply log the request so the
    view layer has a seam we can swap out without changing API contracts.
    """

    LOGGER.info(
        "Queue planet generation", extra={"planet_id": planet_id, "appearance_id": appearance_id}
    )
