from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from media_catalog.models import IdentityTag


class QueerFilmTeaserViewTests(APITestCase):
    @mock.patch("frontend.api.fetch_random_queer_movie")
    def test_returns_movie_payload(self, mock_fetch) -> None:
        mock_fetch.return_value = {
            "title": "Starshine",
            "directors": ["Director Q"],
            "cast": ["Actor A"],
            "release_year": "2022",
        }

        response = self.client.get(reverse("frontend:queer-film-teaser"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["directors"], ["Director Q"])

    @mock.patch("frontend.api.fetch_random_queer_movie", return_value=None)
    def test_returns_service_unavailable_when_missing(self, mock_fetch) -> None:
        response = self.client.get(reverse("frontend:queer-film-teaser"))

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("detail", response.json())


class FeedCarouselRefreshViewTests(APITestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user("astro", password="orbit-strong-42")
        IdentityTag.objects.get_or_create(slug="trans-joy", defaults={"name": "Transidentités"})

    def test_requires_authentication(self) -> None:
        url = reverse("frontend:feed-carousel-refresh", kwargs={"slug": "trans-joy"})
        response = self.client.post(url, {"limit": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch("frontend.api.build_feed_carousel")
    def test_returns_serialized_carousel(self, mock_build) -> None:
        mock_build.return_value = {"theme": "trans-joy", "title": "Transidentités", "items": []}
        self.client.force_authenticate(self.user)
        url = reverse("frontend:feed-carousel-refresh", kwargs={"slug": "trans-joy"})

        response = self.client.post(url, {"limit": 6}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["carousel"]["theme"], "trans-joy")
        mock_build.assert_called_once()

    @mock.patch("frontend.api.build_feed_carousel", return_value=None)
    def test_returns_404_for_unknown_theme(self, mock_build) -> None:
        self.client.force_authenticate(self.user)
        url = reverse("frontend:feed-carousel-refresh", kwargs={"slug": "unknown"})

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_invalid_limit(self) -> None:
        self.client.force_authenticate(self.user)
        url = reverse("frontend:feed-carousel-refresh", kwargs={"slug": "trans-joy"})

        response = self.client.post(url, {"limit": "abc"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
