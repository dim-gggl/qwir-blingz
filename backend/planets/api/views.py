from typing import Any, Dict

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Planet, PlanetAppearance, PlanetMembership
from ..services import (
    PLANET_BUILDER_STEPS,
    apply_state_to_appearance,
    get_or_create_session,
    session_to_state,
    state_to_session,
)
from ..tasks import enqueue_planet_generation
from .serializers import (
    BuilderStateSerializer,
    ConfirmationSerializer,
    NavigationSerializer,
    StepSubmissionSerializer,
)


class IsPlanetOwner(permissions.BasePermission):
    """Allow actions only for the planet creator or designated stewards."""

    def has_object_permission(self, request, view, obj: Planet) -> bool:  # type: ignore[override]
        if request.user.is_anonymous:  # pragma: no cover - DRF handles earlier
            return False
        if obj.created_by_id == request.user.id:
            return True
        return PlanetMembership.objects.filter(
            planet=obj,
            user=request.user,
            role__in=(
                PlanetMembership.ROLE_OWNER,
                PlanetMembership.ROLE_STEWARD,
            ),
        ).exists()


class PlanetBuilderViewSet(viewsets.ViewSet):
    """API endpoints for the planet builder conversation."""

    permission_classes = [permissions.IsAuthenticated, IsPlanetOwner]

    def _get_planet(self, planet_pk: int) -> Planet:
        planet = get_object_or_404(Planet, pk=planet_pk)
        self.check_object_permissions(self.request, planet)
        return planet

    def _serialize_state(self, *, planet: Planet, state) -> Dict[str, Any]:
        serializer = BuilderStateSerializer.from_state(state)
        payload = serializer.data
        payload["planet"] = {
            "id": planet.pk,
            "name": planet.name,
            "slug": planet.slug,
        }
        return payload

    @action(detail=True, methods=["post"], url_path="builder/start")
    def start(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)

        return Response(self._serialize_state(planet=planet, state=state))

    @action(detail=True, methods=["get"], url_path="builder/state")
    def state(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)
        return Response(self._serialize_state(planet=planet, state=state))

    @action(detail=True, methods=["post"], url_path="builder/step")
    def submit_step(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)
        step = PLANET_BUILDER_STEPS[state.step_index]

        serializer = StepSubmissionSerializer(data=request.data, context={"step": step})
        serializer.is_valid(raise_exception=True)
        attrs = serializer.validated_data.get("attributes", {})
        advance = serializer.validated_data.get("advance", True)

        state.set_values(**attrs)
        if advance:
            state.advance()

        state_to_session(session, state)

        appearance = self._get_or_create_appearance(planet)
        apply_state_to_appearance(state=state, appearance=appearance, save=True)
        self._sync_trigger_tags(appearance, state.attributes)

        return Response(self._serialize_state(planet=planet, state=state))

    @action(detail=True, methods=["post"], url_path="builder/skip")
    def skip(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)

        state.mark_skipped()
        state.advance()
        state_to_session(session, state)

        return Response(self._serialize_state(planet=planet, state=state))

    @action(detail=True, methods=["post"], url_path="builder/back")
    def back(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)
        state.retreat()
        state_to_session(session, state)
        return Response(self._serialize_state(planet=planet, state=state))

    @action(detail=True, methods=["post"], url_path="builder/goto")
    def goto(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        serializer = NavigationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_step = serializer.validated_data.get("target_step")

        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)
        if target_step:
            state.goto(target_step)
        state_to_session(session, state)
        return Response(self._serialize_state(planet=planet, state=state))

    @action(detail=True, methods=["post"], url_path="builder/confirm")
    def confirm(self, request, pk: int = None) -> Response:
        planet = self._get_planet(pk)
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data.get("approve"):
            return Response(
                {"detail": "Planet launch cancelled."},
                status=status.HTTP_202_ACCEPTED,
            )

        session = get_or_create_session(planet=planet, user=request.user)
        state = session_to_state(session)

        appearance = self._get_or_create_appearance(planet)
        apply_state_to_appearance(state=state, appearance=appearance, save=True)
        self._sync_trigger_tags(appearance, state.attributes)

        appearance.status = PlanetAppearance.Status.GENERATING
        appearance.save(update_fields=["status", "updated_at"])

        enqueue_planet_generation(planet_id=planet.pk)

        session.is_active = False
        session.save(update_fields=["is_active", "updated_at"])

        payload = self._serialize_state(planet=planet, state=state)
        payload["appearance_status"] = appearance.status
        return Response(payload)

    def _get_or_create_appearance(self, planet: Planet) -> PlanetAppearance:
        appearance, _ = PlanetAppearance.objects.get_or_create(
            planet=planet,
            defaults={
                "name": planet.name,
                "primary_color": planet.accent_color or "#8B5CF6",
            },
        )
        return appearance

    def _sync_trigger_tags(self, appearance: PlanetAppearance, attributes: Dict[str, Any]) -> None:
        tag_ids = attributes.get("trigger_avoidance_tags")
        if tag_ids is None:
            return
        appearance.trigger_avoidance_tags.set(tag_ids)
