from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from media_catalog.models import IdentityTag, MediaItem, MediaList, MediaListItem


class MediaListAPITestCase(APITestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.curator = User.objects.create_user("curator", password="pass-strong-42")
        self.other_user = User.objects.create_user("viewer", password="pass-strong-42")
        self.tag, _ = IdentityTag.objects.get_or_create(
            slug="trans-joy",
            defaults={"name": "Transidentités"},
        )

    def _create_media_list(self, *, owner, visibility=MediaList.VISIBILITY_PUBLIC) -> MediaList:
        media_list = MediaList.objects.create(
            title="Trans Joy Spotlight",
            slug="trans-joy-spotlight-1",
            description="Celebrate trans joy across the galaxy",
            owner=owner,
            visibility=visibility,
            is_dynamic=True,
            source_keyword=self.tag,
        )
        item = MediaItem.objects.create(
            tmdb_id=321,
            title="Joyful Nebula",
            media_type=MediaItem.MEDIA_TYPE_MOVIE,
            overview="A love letter to trans celebration.",
        )
        MediaListItem.objects.create(media_list=media_list, media_item=item, position=1)
        return media_list

    def test_generate_media_list_invokes_service(self) -> None:
        media_list = self._create_media_list(owner=self.curator)
        url = reverse("media-list-list")
        payload = {
            "identity_tag": self.tag.id,
            "limit": 8,
            "visibility": MediaList.VISIBILITY_PUBLIC,
        }

        self.client.force_authenticate(self.curator)
        with patch("media_catalog.api.views.generate_media_list_for_identity") as generate_mock:
            generate_mock.return_value = media_list

            response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        generate_mock.assert_called_once()
        args, kwargs = generate_mock.call_args
        self.assertEqual(kwargs["owner"], self.curator)
        self.assertEqual(kwargs["tag"], self.tag)
        self.assertEqual(kwargs["limit"], 8)

        data = response.json()
        self.assertEqual(data["slug"], media_list.slug)
        self.assertEqual(len(data["items"]), 1)

    def test_public_media_list_is_shareable(self) -> None:
        media_list = self._create_media_list(owner=self.curator, visibility=MediaList.VISIBILITY_PUBLIC)
        url = reverse("media-list-detail", kwargs={"slug": media_list.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["slug"], media_list.slug)
        self.assertEqual(len(data["items"]), 1)

    def test_private_media_list_hidden_from_other_members(self) -> None:
        private_list = self._create_media_list(owner=self.curator, visibility=MediaList.VISIBILITY_PRIVATE)
        url = reverse("media-list-detail", kwargs={"slug": private_list.slug})

        self.client.force_authenticate(self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_update_visibility(self) -> None:
        media_list = self._create_media_list(owner=self.curator, visibility=MediaList.VISIBILITY_PRIVATE)
        url = reverse("media-list-detail", kwargs={"slug": media_list.slug})
        payload = {"visibility": MediaList.VISIBILITY_PUBLIC}

        self.client.force_authenticate(self.curator)
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        media_list.refresh_from_db()
        self.assertEqual(media_list.visibility, MediaList.VISIBILITY_PUBLIC)

    def test_refresh_calls_generator_again(self) -> None:
        media_list = self._create_media_list(owner=self.curator, visibility=MediaList.VISIBILITY_PUBLIC)
        url = reverse("media-list-refresh", kwargs={"slug": media_list.slug})

        self.client.force_authenticate(self.curator)
        with patch("media_catalog.api.views.generate_media_list_for_identity") as generate_mock:
            generate_mock.return_value = media_list
            response = self.client.post(url, {"limit": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        generate_mock.assert_called_once()
        args, kwargs = generate_mock.call_args
        self.assertEqual(kwargs["limit"], 3)
        self.assertEqual(kwargs["tag"], self.tag)
