from __future__ import annotations

from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import TriggerTopic, User
from planets.models import Planet, PlanetAppearance


class PlanetBuilderViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create_user(username="owner", password="strong-pass")
        self.other = User.objects.create_user(username="other", password="strong-pass")
        self.trigger_topic = TriggerTopic.objects.create(name="loud sounds", slug="loud-sounds")

        self.planet = Planet.objects.create(
            name="Echo", slug="echo",
            created_by=self.owner,
            accent_color="#FF00AA",
        )
        self.client.force_authenticate(self.owner)

    def _url(self, action: str) -> str:
        name_map = {
            'start': 'planet-builder-start',
            'state': 'planet-builder-state',
            'step': 'planet-builder-submit-step',
            'skip': 'planet-builder-skip',
            'back': 'planet-builder-back',
            'goto': 'planet-builder-goto',
            'confirm': 'planet-builder-confirm',
        }
        return reverse(name_map[action], kwargs={'pk': self.planet.pk})

    def test_start_initializes_session(self) -> None:
        response = self.client.post(self._url("start"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["step_index"], 0)
        self.assertIn("planet", response.data)

    def test_submit_step_updates_state(self) -> None:
        self.client.post(self._url("start"))
        payload = {
            "attributes": {
                "name": "Echo",
                "tagline": "Vibrant echoes",
                "motto": "Resonance forever",
            }
        }
        response = self.client.post(self._url("step"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["step_index"], 1)

        appearance = PlanetAppearance.objects.get(planet=self.planet)
        self.assertEqual(appearance.name, "Echo")
        self.assertEqual(appearance.tagline, "Vibrant echoes")

    def test_confirm_enqueues_generation(self) -> None:
        self.client.post(self._url("start"))
        self.client.post(
            self._url("step"),
            {"attributes": {"name": "Echo", "tagline": "Vibe", "motto": "Glow"}},
            format="json",
        )
        self.client.post(
            self._url("step"),
            {"attributes": {"emotional_tone": "sanctuary"}},
            format="json",
        )
        with mock.patch("planets.api.views.enqueue_planet_generation") as mocked_enqueue:
            response = self.client.post(
                self._url("confirm"),
                {"approve": True},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appearance = PlanetAppearance.objects.get(planet=self.planet)
        self.assertEqual(appearance.status, PlanetAppearance.Status.GENERATING)
        mocked_enqueue.assert_called_once()

    def test_permissions_block_non_owner(self) -> None:
        self.client.force_authenticate(self.other)
        response = self.client.post(self._url("start"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
