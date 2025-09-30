from __future__ import annotations

from typing import Dict, List, Optional

from django.contrib.auth import get_user_model
from django.test import TestCase

from media_catalog.models import IdentityTag, MediaItem
from media_catalog.services import generate_media_list_for_identity
from media_catalog.services.generator import DEFAULT_APPEND
from tmdb import TmdbNotFoundError


class FakeTmdbClient:
    """Simple test double for the TMDb client interface."""

    def __init__(
        self,
        *,
        keyword_id: int = 314,
        search_results: Optional[List[Dict[str, object]]] = None,
        discover_batches: Optional[List[Dict[str, object]]] = None,
        details: Optional[Dict[int, Dict[str, object]]] = None,
    ) -> None:
        self.keyword_id = keyword_id
        self.search_results = search_results or []
        self.discover_batches = discover_batches or []
        self.details = details or {}

        self.search_calls: List[str] = []
        self.discover_calls: List[Dict[str, object]] = []
        self.detail_calls: List[int] = []

    def search_keyword(self, query: str, *, page: int = 1) -> Dict[str, object]:
        self.search_calls.append(query)
        if self.search_results:
            return {"results": self.search_results}
        return {"results": [{"id": self.keyword_id, "name": query}]}

    def discover_movies(self, **params) -> Dict[str, object]:
        self.discover_calls.append(params)
        if self.discover_batches:
            return self.discover_batches.pop(0)
        return {"results": [], "total_pages": 0}

    def get_movie_details(self, movie_id: int, *, append_to_response: Optional[str] = None) -> Dict[str, object]:
        self.detail_calls.append(movie_id)
        payload = self.details.get(movie_id)
        if payload is None:
            raise AssertionError(f"Unexpected TMDb detail lookup for id {movie_id}")
        if append_to_response:
            payload = {**payload, "_append": append_to_response}
        return payload


class GenerateMediaListServiceTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user("film-curator", password="strong-pass-123")
        self.tag = IdentityTag.objects.create(name="Trans Joy", slug="trans-joy")

    def test_generates_media_list_and_persists_keyword(self) -> None:
        summary = {
            "id": 42,
            "title": "A Trans Tale",
            "overview": "Finding community among the stars.",
            "poster_path": "/poster.jpg",
            "backdrop_path": "/backdrop.jpg",
            "release_date": "2023-04-01",
        }
        details = {
            "id": 42,
            "title": "A Trans Tale",
            "overview": "Finding community among the stars.",
            "poster_path": "/poster.jpg",
            "backdrop_path": "/backdrop.jpg",
            "release_date": "2023-04-01",
        }
        client = FakeTmdbClient(
            keyword_id=777,
            discover_batches=[{"results": [summary], "total_pages": 1}],
            details={42: details},
        )

        media_list = generate_media_list_for_identity(
            tag=self.tag,
            owner=self.user,
            limit=3,
            client=client,
        )

        self.assertEqual(self.tag.tmdb_keyword_id, 777)
        self.assertEqual(media_list.source_keyword_id, self.tag.id)
        self.assertEqual(media_list.items.count(), 1)

        list_item = media_list.items.select_related("media_item").first()
        assert list_item is not None
        media_item = list_item.media_item
        self.assertEqual(media_item.tmdb_id, 42)
        self.assertEqual(media_item.title, "A Trans Tale")
        self.assertEqual(media_item.release_date.year, 2023)
        self.assertIn(self.tag, media_item.identity_tags.all())

        self.assertEqual(client.detail_calls, [42])
        self.assertEqual(
            media_item.metadata["details"].get("_append"),
            DEFAULT_APPEND,
        )

    def test_refresh_updates_existing_media_items(self) -> None:
        self.tag.tmdb_keyword_id = 888
        self.tag.save(update_fields=["tmdb_keyword_id"])

        initial_summary = {
            "id": 11,
            "title": "First Cut",
            "overview": "An indie doc about ballroom origins.",
            "poster_path": "/poster-old.jpg",
            "release_date": "2020-01-01",
        }
        initial_details = {
            "id": 11,
            "title": "First Cut",
            "overview": "An indie doc about ballroom origins.",
            "poster_path": "/poster-old.jpg",
            "release_date": "2020-01-01",
        }
        client_initial = FakeTmdbClient(
            keyword_id=888,
            discover_batches=[{"results": [initial_summary], "total_pages": 1}],
            details={11: initial_details},
        )
        generate_media_list_for_identity(tag=self.tag, owner=self.user, limit=1, client=client_initial)

        refreshed_summary = {
            "id": 11,
            "title": "First Cut (Remastered)",
            "overview": "Restored footage and richer interviews.",
            "poster_path": "/poster-new.jpg",
            "release_date": "2020-01-01",
        }
        refreshed_details = {
            "id": 11,
            "title": "First Cut (Remastered)",
            "overview": "Restored footage and richer interviews.",
            "poster_path": "/poster-new.jpg",
            "release_date": "2020-01-01",
        }
        client_refresh = FakeTmdbClient(
            keyword_id=888,
            discover_batches=[{"results": [refreshed_summary], "total_pages": 1}],
            details={11: refreshed_details},
        )
        media_list = generate_media_list_for_identity(tag=self.tag, owner=self.user, limit=1, client=client_refresh)

        media_item = MediaItem.objects.get(tmdb_id=11)
        self.assertEqual(media_item.title, "First Cut (Remastered)")
        self.assertEqual(media_item.metadata["details"]["title"], "First Cut (Remastered)")
        self.assertEqual(media_list.items.count(), 1)
        list_item = media_list.items.first()
        self.assertIsNotNone(list_item)
        if list_item:
            self.assertEqual(list_item.position, 1)

    def test_raises_when_no_results(self) -> None:
        client = FakeTmdbClient(discover_batches=[{"results": [], "total_pages": 0}])

        with self.assertRaises(TmdbNotFoundError):
            generate_media_list_for_identity(tag=self.tag, owner=self.user, client=client)
