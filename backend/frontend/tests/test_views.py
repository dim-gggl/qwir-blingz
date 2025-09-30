from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ThemeDetailViewTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user("member", password="constellation42")

    def test_requires_authentication(self) -> None:
        response = self.client.get(reverse("frontend:theme-detail", kwargs={"slug": "trans-joy"}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    @mock.patch("frontend.views.build_theme_detail")
    def test_renders_theme_detail(self, mock_build) -> None:
        mock_build.return_value = {
            "theme": "trans-joy",
            "title": "Transidentités",
            "description": "",
            "feature": None,
            "sections": [],
            "fallback": False,
            "items_count": 0,
            "source_keyword": None,
            "list_slug": None,
        }
        self.client.force_login(self.user)

        response = self.client.get(reverse("frontend:theme-detail", kwargs={"slug": "trans-joy"}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transidentités")
        mock_build.assert_called_once()

    @mock.patch("frontend.views.build_theme_detail", return_value=None)
    def test_returns_404_when_missing(self, mock_build) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("frontend:theme-detail", kwargs={"slug": "unknown"}))
        self.assertEqual(response.status_code, 404)
