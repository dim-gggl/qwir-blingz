from __future__ import annotations

from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


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
