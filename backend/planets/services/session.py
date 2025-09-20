"""Utilities for persisting planet builder state."""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import Planet, PlanetAppearance, PlanetBuilderSession
from .builder import PlanetBuilderState

User = get_user_model()


def session_to_state(session: PlanetBuilderSession) -> PlanetBuilderState:
    """Convert a stored session into an in-memory state object."""

    return PlanetBuilderState(
        planet_id=session.planet_id,
        step_index=session.step_index,
        attributes=dict(session.attributes or {}),
        skipped_steps=list(session.skipped_steps or []),
        confirmations=dict(session.confirmations or {}),
    )


@transaction.atomic
def state_to_session(
    session: PlanetBuilderSession,
    state: PlanetBuilderState,
    *,
    save: bool = True,
) -> PlanetBuilderSession:
    """Persist an in-memory state back to the database session."""

    session.step_index = state.step_index
    session.attributes = dict(state.attributes)
    session.skipped_steps = list(state.skipped_steps)
    session.confirmations = dict(state.confirmations)
    if save:
        session.save(update_fields=[
            "step_index",
            "attributes",
            "skipped_steps",
            "confirmations",
            "updated_at",
        ])
    return session


@transaction.atomic
def get_or_create_session(
    *,
    planet: Planet,
    user: User,
    reset: bool = False,
) -> PlanetBuilderSession:
    """Fetch the existing session or create/reset it for the builder."""

    session, created = PlanetBuilderSession.objects.get_or_create(
        planet=planet,
        defaults={
            "user": user,
        },
    )
    if not created and reset:
        session.reset()
    elif created:
        session.user = user
        session.save(update_fields=["user", "updated_at"])
    return session


def apply_state_to_appearance(
    *,
    state: PlanetBuilderState,
    appearance: PlanetAppearance,
    save: bool = True,
) -> PlanetAppearance:
    """Copy collected attributes into the PlanetAppearance draft object."""

    attrs = state.attributes

    simple_fields = [
        "name",
        "tagline",
        "motto",
        "primary_color",
        "secondary_color",
        "surface_type",
        "ring_style",
        "ring_color",
        "has_moons",
        "moon_count",
        "atmosphere_style",
        "origin_type",
        "emotional_tone",
        "emotional_custom_label",
        "accessibility_notes",
    ]
    for field in simple_fields:
        value = attrs.get(field)
        if value is not None:
            setattr(appearance, field, value)

    list_fields = {
        "palette": list,
        "surface_descriptors": list,
        "ring_descriptors": list,
        "moon_descriptors": list,
        "atmosphere_descriptors": list,
        "materials": list,
        "custom_trigger_warnings": list,
    }
    for field, caster in list_fields.items():
        if field in attrs:
            value = attrs.get(field)
            setattr(appearance, field, caster(value) if value is not None else [])

    # Many-to-many trigger tags handled separately by the view/serializer since
    # it requires saving before assignment.

    if save:
        appearance.status = PlanetAppearance.Status.DRAFT
        appearance.save()
    return appearance
