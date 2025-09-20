from __future__ import annotations

from unittest import mock

from django.test import SimpleTestCase

from frontend.services import fetch_random_queer_movie, normalize_movie_payload


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

    @mock.patch("frontend.services.get_tmdb_client")
    def test_returns_none_when_client_missing(
        self,
        mock_get_tmdb_client: mock.MagicMock,
    ) -> None:
        mock_get_tmdb_client.side_effect = ValueError("missing API key")

        movie = fetch_random_queer_movie()

        self.assertIsNone(movie)
