from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from frontend.fallbacks import FALLBACK_QUEER_MOVIES
from frontend.services import (
    build_feed_carousel,
    build_theme_detail,
    fetch_random_queer_movie,
    normalize_movie_payload,
)
from media_catalog.models import IdentityTag, MediaItem, MediaList, MediaListItem


class NormalizeMoviePayloadTests(SimpleTestCase):
    def test_extracts_release_year_directors_and_cast(self) -> None:
        payload = {
            "movie": {
                "id": 42,
                "title": "Glitter Nova",
                "original_title": "Nova Brillante",
                "overview": "A cosmic queer rebellion.",
                "poster_path": "/poster.jpg",
                "backdrop_path": "/backdrop.jpg",
                "release_date": "2023-05-17",
                "original_language": "fr",
                "production_countries": [{"name": "France"}],
                "vote_average": 7.8,
                "vote_count": 1200,
                "credits": {
                    "cast": [
                        {"name": "Star Kid"},
                        {"name": "Moon Babe"},
                    ],
                    "crew": [
                        {"name": "A. Director", "job": "Director"},
                        {"name": "B. Helper", "department": "Directing"},
                    ],
                },
                "external_ids": {"imdb_id": "tt1234567"},
            },
            "summary": {
                "release_date": "2023-05-17",
            },
        }

        normalized = normalize_movie_payload(payload)

        self.assertEqual(normalized["release_year"], "2023")
        self.assertEqual(normalized["directors"], ["A. Director", "B. Helper"])
        self.assertEqual(normalized["cast"], ["Star Kid", "Moon Babe"])
        self.assertTrue(normalized["poster_url"].endswith("/poster.jpg"))


class FetchRandomQueerMovieTests(SimpleTestCase):
    @mock.patch("frontend.services.sample_movie_by_keyword")
    @mock.patch("frontend.services.get_tmdb_client")
    def test_fetch_random_movie_returns_normalized_payload(
        self,
        mock_get_tmdb_client: mock.MagicMock,
        mock_sample_movie: mock.MagicMock,
    ) -> None:
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        mock_get_tmdb_client.return_value = client
        mock_sample_movie.return_value = {
            "movie": {
                "id": 99,
                "title": "Queer Nebula",
                "release_date": "2020-01-01",
                "credits": {
                    "cast": [{"name": "Lead"}],
                    "crew": [{"name": "Director X", "job": "Director"}],
                },
            },
            "summary": {
                "release_date": "2020-01-01",
            },
        }

        movie = fetch_random_queer_movie()

        self.assertIsNotNone(movie)
        assert movie is not None
        self.assertEqual(movie["directors"], ["Director X"])
        self.assertEqual(movie["cast"], ["Lead"])
        mock_sample_movie.assert_called_once()
        self.assertEqual(
            mock_sample_movie.call_args[1]["append_to_response"],
            "credits,external_ids",
        )

    @mock.patch("frontend.services.random.choice")
    @mock.patch("frontend.services.get_tmdb_client")
    def test_returns_fallback_when_client_missing(
        self,
        mock_get_tmdb_client: mock.MagicMock,
        mock_choice: mock.MagicMock,
    ) -> None:
        mock_get_tmdb_client.side_effect = ValueError("missing API key")
        mock_choice.return_value = FALLBACK_QUEER_MOVIES[0]

        movie = fetch_random_queer_movie()

        self.assertIsNotNone(movie)
        assert movie is not None
        self.assertEqual(movie["title"], FALLBACK_QUEER_MOVIES[0]["title"])
        mock_choice.assert_called_once()


class BuildFeedCarouselTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user("astro", password="orbit-strong-42")
        self.tag, _ = IdentityTag.objects.get_or_create(
            slug="trans-joy",
            defaults={"name": "Transidentités"},
        )

        self.media_item = MediaItem.objects.create(
            tmdb_id=999,
            title="Joyful Nebula",
            media_type=MediaItem.MEDIA_TYPE_MOVIE,
            overview="Une odyssée trans lumineuse.",
            metadata={
                "summary": {
                    "overview": "Résumé", "poster_path": "/poster.jpg", "release_date": "2022-01-01",
                    "vote_average": 7.2,
                },
                "details": {
                    "overview": "Résumé détaillé",
                    "release_date": "2022-01-01",
                    "vote_average": 7.8,
                    "vote_count": 120,
                    "runtime": 96,
                    "genres": [{"name": "Documentaire"}],
                    "credits": {
                        "cast": [{"name": "Actrice Lune"}, {"name": "Performer Soleil"}],
                        "crew": [
                            {"name": "Réalisateur X", "job": "Director"},
                            {"name": "Réalisatrice Y", "department": "Directing"},
                        ],
                    },
                    "similar": {
                        "results": [
                            {"id": 321, "title": "Harmonie", "poster_path": "/harmonie.jpg", "release_date": "2020-02-02"},
                        ]
                    },
                    "watch/providers": {
                        "results": {
                            "FR": {
                                "link": "https://example.com/watch",
                                "flatrate": [
                                    {"provider_name": "FluxMagique", "logo_path": "/logo.png"},
                                ],
                            }
                        }
                    },
                },
            },
        )

        self.media_list = MediaList.objects.create(
            title="Transidentités",
            slug="trans-joy-spotlight",
            description="Sélection",
            owner=self.user,
            visibility=MediaList.VISIBILITY_UNLISTED,
            is_dynamic=True,
            source_keyword=self.tag,
        )
        MediaListItem.objects.create(media_list=self.media_list, media_item=self.media_item, position=1)

    @mock.patch("frontend.services.generate_media_list_for_identity")
    def test_returns_serialized_carousel(self, mock_generate) -> None:
        mock_generate.return_value = self.media_list

        carousel = build_feed_carousel("trans-joy", user=self.user)

        self.assertIsNotNone(carousel)
        assert carousel is not None
        self.assertEqual(carousel["theme"], "trans-joy")
        self.assertEqual(carousel["title"], "Transidentités")
        self.assertEqual(len(carousel["items"]), 1)
        item = carousel["items"][0]
        self.assertEqual(item["title"], "Joyful Nebula")
        self.assertTrue(item["watch"]["providers"])
        self.assertTrue(item["similar"])

    def test_returns_fallback_when_tag_missing(self) -> None:
        carousel = build_feed_carousel("lesbian-love", user=self.user)

        self.assertIsNotNone(carousel)
        assert carousel is not None
        self.assertTrue(carousel.get("fallback"))
        self.assertEqual(carousel["theme"], "lesbian-love")


class BuildThemeDetailTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user("astro", password="orbit-strong-42")
        self.tag, _ = IdentityTag.objects.get_or_create(
            slug="trans-joy",
            defaults={"name": "Transidentités"},
        )

        self.media_item = MediaItem.objects.create(
            tmdb_id=555,
            title="Orbiting Joy",
            media_type=MediaItem.MEDIA_TYPE_MOVIE,
            overview="Une odyssée trans galactique.",
            metadata={
                "summary": {"poster_path": "/poster.jpg", "release_date": "2022-01-01"},
                "details": {
                    "overview": "Résumé détaillé",
                    "release_date": "2022-01-01",
                    "runtime": 40,
                    "vote_average": 7.8,
                    "vote_count": 120,
                    "genres": [{"name": "Documentary"}, {"name": "Drama"}],
                    "credits": {
                        "cast": [{"name": "Acteur•ice Nova"}],
                        "crew": [{"name": "Capitaine X", "job": "Director"}],
                    },
                    "similar": {
                        "results": [
                            {"id": 777, "title": "Comète", "poster_path": "/comete.jpg", "release_date": "2021-04-01"}
                        ]
                    },
                    "watch/providers": {
                        "results": {
                            "FR": {
                                "link": "https://example.com/watch",
                                "flatrate": [{"provider_name": "StreamQueer", "logo_path": "/logo.png"}],
                            }
                        }
                    },
                },
            },
        )

        self.media_list = MediaList.objects.create(
            title="Transidentités",
            slug="trans-joy-spotlight",
            description="Sélection",
            owner=self.user,
            visibility=MediaList.VISIBILITY_UNLISTED,
            is_dynamic=True,
            source_keyword=self.tag,
        )
        MediaListItem.objects.create(media_list=self.media_list, media_item=self.media_item, position=1)

    @mock.patch("frontend.services.generate_media_list_for_identity")
    def test_returns_sections_and_feature(self, mock_generate) -> None:
        mock_generate.return_value = self.media_list

        detail = build_theme_detail("trans-joy", user=self.user, limit=10)

        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(detail["theme"], "trans-joy")
        self.assertFalse(detail["fallback"])
        self.assertIsNotNone(detail["feature"])
        section_titles = [section["title"] for section in detail["sections"]]
        self.assertIn("Courts métrages", section_titles)
        self.assertIn("Documentaires & essais", section_titles)

    def test_fallback_when_no_tag(self) -> None:
        detail = build_theme_detail("lesbian-love", user=self.user)
        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertTrue(detail["fallback"])
