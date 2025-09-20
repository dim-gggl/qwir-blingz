from __future__ import annotations

from typing import Any, Dict, Optional

from tmdb import TmdbClient
from tmdb.exceptions import TmdbError
from tmdb.services import sample_movie_by_keyword
from tmdb.utils import get_tmdb_client

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


def _build_poster_url(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return f"{POSTER_BASE_URL}{path}"


def normalize_movie_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    movie = payload.get("movie", {})
    summary = payload.get("summary", {})

    release_date = movie.get("release_date") or summary.get("release_date")
    release_year = release_date.split("-")[0] if release_date else None
    original_title = movie.get("original_title") or summary.get("original_title")
    origin_country = (movie.get("production_countries") or summary.get("production_countries") or [])
    origin_country = origin_country[0]["name"] if origin_country else None
    original_language = movie.get("original_language") or summary.get("original_language")

    credits = movie.get("credits", {}) if isinstance(movie.get("credits"), dict) else {}
    cast = credits.get("cast") or []
    top_cast = [person.get("name") for person in cast[:4] if person.get("name")]

    crew = credits.get("crew") or []
    directors = [member.get("name") for member in crew if member.get("job") == "Director" and member.get("name")]
    if not directors:
        directors = [
            member.get("name")
            for member in crew
            if member.get("department") == "Directing" and member.get("name")
        ]
    # Dedupe while preserving order
    seen = set()
    directors = [name for name in directors if not (name in seen or seen.add(name))]

    rating = movie.get("vote_average") or summary.get("vote_average")
    vote_count = movie.get("vote_count") or summary.get("vote_count")

    external_ids = movie.get("external_ids") or {}

    tmdb_id = movie.get("id") or summary.get("id")
    imdb_id = external_ids.get("imdb_id")

    return {
        "title": movie.get("title") or summary.get("title"),
        "original_title": original_title if original_title and original_title != (movie.get("title") or summary.get("title")) else None,
        "tagline": movie.get("tagline"),
        "overview": movie.get("overview") or summary.get("overview"),
        "poster_url": _build_poster_url(movie.get("poster_path") or summary.get("poster_path")),
        "backdrop_url": _build_poster_url(movie.get("backdrop_path") or summary.get("backdrop_path")),
        "release_year": release_year,
        "origin_country": origin_country,
        "original_language": original_language,
        "cast": top_cast,
        "rating": rating,
        "vote_count": vote_count,
        "directors": directors,
        "tmdb_id": tmdb_id,
        "tmdb_url": f"https://www.themoviedb.org/movie/{tmdb_id}" if tmdb_id else None,
        "imdb_id": imdb_id,
        "imdb_url": f"https://www.imdb.com/title/{imdb_id}" if imdb_id else None,
    }


def fetch_random_queer_movie() -> Optional[Dict[str, Any]]:
    client: Optional[TmdbClient]
    try:
        client = get_tmdb_client()
    except ValueError:
        return None

    if not client:
        return None

    try:
        with client:
            payload = sample_movie_by_keyword(
                client,
                "Queer",
                append_to_response="credits,external_ids",
            )
    except TmdbError:
        return None

    normalized = normalize_movie_payload(payload)
    if normalized:
        if not normalized.get("cast"):
            summary = payload.get("summary", {}) or {}
            cast = summary.get("cast") or []
            normalized["cast"] = [person.get("name") for person in cast[:4] if person.get("name")]
        if normalized.get("directors") is None:
            normalized["directors"] = []
    return normalized
