from typing import Any, Dict, List

from rest_framework import serializers

from accounts.models import TriggerTopic
from ..models import PlanetAppearance
from ..services import (
    PLANET_BUILDER_STEPS,
    BuilderStep,
    PlanetBuilderState,
)

HEX_COLOR_LENGTH = 7


class BuilderStateSerializer(serializers.Serializer):
    planet_id = serializers.IntegerField()
    step_index = serializers.IntegerField()
    attributes = serializers.DictField(child=serializers.JSONField(), default=dict)
    skipped_steps = serializers.ListField(child=serializers.CharField(), default=list)
    confirmations = serializers.DictField(child=serializers.BooleanField(), default=dict)
    current_step = serializers.SerializerMethodField()

    def get_current_step(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        idx = obj.get("step_index", 0)
        idx = max(0, min(idx, len(PLANET_BUILDER_STEPS) - 1))
        step = PLANET_BUILDER_STEPS[idx]
        return {
            "id": step.id,
            "title": step.title,
            "prompt": step.prompt,
            "input_type": step.input_type.value,
            "suggestions": step.suggestions,
            "optional": step.optional,
        }

    @classmethod
    def from_state(cls, state: PlanetBuilderState) -> "BuilderStateSerializer":
        data = {
            "planet_id": state.planet_id,
            "step_index": state.step_index,
            "attributes": state.attributes,
            "skipped_steps": state.skipped_steps,
            "confirmations": state.confirmations,
        }
        return cls(data)


class StepSubmissionSerializer(serializers.Serializer):
    attributes = serializers.DictField(child=serializers.JSONField(), required=True)
    advance = serializers.BooleanField(default=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        step: BuilderStep | None = self.context.get("step")
        if not step:
            return attrs
        data = dict(attrs)
        payload = data.get("attributes", {})
        validated = self._validate_step_payload(step, payload)
        data["attributes"] = validated
        return data

    def _validate_step_payload(self, step: BuilderStep, payload: Dict[str, Any]) -> Dict[str, Any]:
        if step.id == "intro":
            name = str(payload.get("name", "")).strip()
            if not name:
                raise serializers.ValidationError({"attributes": {"name": "Planet name is required."}})
        elif step.id == "tone":
            tone = payload.get("emotional_tone")
            if tone not in PlanetAppearance.EmotionalTone.values:
                raise serializers.ValidationError({"attributes": {"emotional_tone": "Invalid emotional tone."}})
            if (
                tone == PlanetAppearance.EmotionalTone.CUSTOM
                and not str(payload.get("emotional_custom_label", "")).strip()
            ):
                raise serializers.ValidationError(
                    {"attributes": {"emotional_custom_label": "Describe your custom tone."}}
                )
        elif step.id == "palette":
            self._ensure_hex_color(payload.get("primary_color"), field="primary_color")
            secondary = payload.get("secondary_color")
            if secondary:
                self._ensure_hex_color(secondary, field="secondary_color")
            palette = payload.get("palette")
            if palette is not None and not isinstance(palette, list):
                raise serializers.ValidationError(
                    {"attributes": {"palette": "Palette must be a list of color entries."}}
                )
        elif step.id == "surface":
            surface_type = payload.get("surface_type")
            if surface_type not in PlanetAppearance.SurfaceType.values:
                raise serializers.ValidationError(
                    {"attributes": {"surface_type": "Choose a valid surface type."}}
                )
        elif step.id == "atmosphere":
            style = payload.get("atmosphere_style")
            if style not in PlanetAppearance.AtmosphereStyle.values:
                raise serializers.ValidationError(
                    {"attributes": {"atmosphere_style": "Choose a valid atmosphere style."}}
                )
        elif step.id == "safety":
            payload["trigger_avoidance_tags"] = self._validate_trigger_tags(
                payload.get("trigger_avoidance_tags")
            )
            warnings = payload.get("custom_trigger_warnings")
            if warnings is not None and not isinstance(warnings, list):
                raise serializers.ValidationError(
                    {"attributes": {"custom_trigger_warnings": "Provide warnings as a list."}}
                )
        moon_count = payload.get("moon_count")
        if moon_count is not None:
            try:
                moon_count = int(moon_count)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {"attributes": {"moon_count": "Moon count must be an integer."}}
                )
            if moon_count < 0:
                raise serializers.ValidationError(
                    {"attributes": {"moon_count": "Moon count cannot be negative."}}
                )
            payload["moon_count"] = moon_count
        return payload

    def _ensure_hex_color(self, value: Any, *, field: str) -> None:
        if not value or not isinstance(value, str):
            raise serializers.ValidationError(
                {"attributes": {field: "Provide a HEX color (e.g., #FF69B4)."}}
            )
        if len(value) != HEX_COLOR_LENGTH or not value.startswith("#"):
            raise serializers.ValidationError(
                {"attributes": {field: "Provide a HEX color (e.g., #FF69B4)."}}
            )
        hex_part = value[1:]
        try:
            int(hex_part, 16)
        except ValueError:
            raise serializers.ValidationError(
                {"attributes": {field: "Provide a HEX color (e.g., #FF69B4)."}}
            )

    def _validate_trigger_tags(self, value: Any) -> List[int]:
        if value in (None, "", []):
            return []
        if not isinstance(value, (list, tuple)):
            raise serializers.ValidationError(
                {"attributes": {"trigger_avoidance_tags": "Submit a list of trigger topic IDs."}}
            )
        try:
            tag_ids = [int(v) for v in value]
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {"attributes": {"trigger_avoidance_tags": "Trigger topic IDs must be integers."}}
            )
        existing = set(
            TriggerTopic.objects.filter(id__in=tag_ids).values_list("id", flat=True)
        )
        missing = [str(v) for v in tag_ids if v not in existing]
        if missing:
            raise serializers.ValidationError(
                {
                    "attributes": {
                        "trigger_avoidance_tags": f"Unknown trigger topic IDs: {', '.join(missing)}"
                    }
                }
            )
        return tag_ids


class NavigationSerializer(serializers.Serializer):
    target_step = serializers.CharField(required=False, allow_blank=True)


class ConfirmationSerializer(serializers.Serializer):
    approve = serializers.BooleanField(required=True)
