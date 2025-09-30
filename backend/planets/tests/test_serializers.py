from django.test import TestCase

from accounts.models import TriggerTopic, User
from planets.api.serializers import StepSubmissionSerializer
from rest_framework.exceptions import ValidationError
from planets.services import PLANET_BUILDER_STEPS


class StepSubmissionSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="tester", password="strong-pass")
        self.trigger_topic = TriggerTopic.objects.create(name="loud sounds", slug="loud-sounds")

    def _serialize_step(self, step_id: str, attributes: dict[str, object], advance: bool = True):
        step = next(step for step in PLANET_BUILDER_STEPS if step.id == step_id)
        serializer = StepSubmissionSerializer(
            data={"attributes": attributes, "advance": advance},
            context={"step": step},
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def test_intro_requires_name(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Planet name is required"):
            self._serialize_step("intro", {})

    def test_tone_requires_valid_choice(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Invalid emotional tone"):
            self._serialize_step("tone", {"emotional_tone": "invalid"})

    def test_tone_custom_requires_label(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Describe your custom tone"):
            self._serialize_step("tone", {"emotional_tone": "custom"})

    def test_palette_requires_hex(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Provide a HEX color"):
            self._serialize_step("palette", {"primary_color": "pink"})

    def test_safety_validates_trigger_topics(self) -> None:
        data = self._serialize_step(
            "safety",
            {"trigger_avoidance_tags": [self.trigger_topic.id], "custom_trigger_warnings": []},
        )
        self.assertEqual(data["attributes"]["trigger_avoidance_tags"], [self.trigger_topic.id])

    def test_moon_count_casts_to_int(self) -> None:
        data = self._serialize_step(
            "rings",
            {
                "ring_style": "single",
                "ring_descriptors": [],
                "ring_color": "#FFFFFF",
                "has_moons": True,
                "moon_count": "2",
                "moon_descriptors": [],
            },
        )
        self.assertEqual(data["attributes"]["moon_count"], 2)

    def test_negative_moon_count_rejected(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Moon count cannot be negative"):
            self._serialize_step("rings", {"moon_count": -1, "ring_style": "none"})
