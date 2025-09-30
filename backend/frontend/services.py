from __future__ import annotations

import random
from typing import Any, Dict, Iterable, List, Optional

from django.conf import settings

from tmdb import TmdbClient
from tmdb.exceptions import TmdbError
from tmdb.services import sample_movie_by_keyword
from tmdb.utils import get_tmdb_client

from media_catalog.models import IdentityTag, MediaList
from media_catalog.services import generate_media_list_for_identity

from .fallbacks import FALLBACK_QUEER_MOVIES, FALLBACK_THEME_LISTS

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w780"

FEED_THEMES: List[Dict[str, str]] = [
    {
        "slug": "trans-joy",
        "title": "Transidentités",
        "fallback": "transidentites",
        "description": "Films et séries centrés sur les expériences et les joies trans.",
    },
    {
        "slug": "lesbian-love",
        "title": "Lesbiennes",
        "fallback": "lesbiennes",
        "description": "Histoires lesbiennes, romances, drames, docs et plus.",
    },
    {
        "slug": "gay-celebration",
        "title": "Gays",
        "fallback": "queers",
        "description": "Créations gays : pride, mémoire, fêtes, luttes et amours.",
    },
    {
        "slug": "queer-joy",
        "title": "Queers",
        "fallback": "queers",
        "description": "Panorama queer : joyeuses galaxies, club kids, ballrooms, résistance.",
    },
    {
        "slug": "lgbt-history",
        "title": "LGBTQIA+",
        "fallback": "queers",
        "description": "Archives et imaginaires LGBTQIA+ intergénérationnels.",
    },
    {
        "slug": "non-binary",
        "title": "Non-binaire",
        "fallback": "transidentites",
        "description": "Identités non-binaires, fluides et genderqueer à l’écran.",
    },
    {
        "slug": "gender-studies",
        "title": "Théories du Genre",
        "fallback": "queers",
        "description": "Essais, docs et fictions qui bousculent les cadres du genre.",
    },
    {
        "slug": "radical-feminism",
        "title": "Féminisme radical",
        "fallback": "lesbiennes",
        "description": "Héritages et combats transféministes décoloniaux.",
    },
    {
        "slug": "intersex",
        "title": "Intersex",
        "fallback": "transidentites",
        "description": "Récits intersexes : lutte, douceur et autodétermination.",
    },
    {
        "slug": "asexual",
        "title": "Asexuel",
        "fallback": "queers",
        "description": "Narrations ace et aromantiques, des contes aux docs.",
    },
    {
        "slug": "tds-sex-work",
        "title": "Travail du sexe",
        "fallback": "queers",
        "description": "Travail du sexe, mutual aid, luttes anti-répression.",
    },
    {
        "slug": "bisexual",
        "title": "Bi",
        "fallback": "queers",
        "description": "Identités bisexuelles, pansexuelles et plurisexuelles à l'écran.",
    },
    {
        "slug": "pansexual",
        "title": "Pan",
        "fallback": "queers",
        "description": "Narrations pansexuelles et polyromantiques, amours sans frontières.",
    },
    {
        "slug": "disability-joy",
        "title": "Joies handies",
        "fallback": "queers",
        "description": "Récits handis, mad pride, neurodivergence et fierté crip.",
    },
    {
        "slug": "bipoc-lgbtq",
        "title": "LGBTQ+ racisé·es",
        "fallback": "queers",
        "description": "Expériences LGBTQ+ racisées, décoloniales et intersectionnelles.",
    },
]


def _normalize_language(language: Optional[str]) -> Optional[str]:
    if not language:
        return None
    normalized = language.replace("_", "-")
    parts = normalized.split("-")
    if len(parts) == 2:
        return f"{parts[0].lower()}-{parts[1].upper()}"
    return normalized


GENRE_CATEGORY_MAP: List[Dict[str, Any]] = [
    {"title": "Horreur & frissons", "match": {"horror"}},
    {"title": "Comédies et feel-good", "match": {"comedy"}},
    {"title": "Documentaires & essais", "match": {"documentary"}},
    {"title": "Science-fiction & fantastique", "match": {"science fiction", "fantasy"}},
    {"title": "Romances & drames", "match": {"romance", "drama"}},
]

def _is_short_form(item: Dict[str, Any]) -> bool:
    runtime = item.get("runtime")
    return isinstance(runtime, (int, float)) and runtime <= 45


def _is_long_form(item: Dict[str, Any]) -> bool:
    runtime = item.get("runtime")
    return isinstance(runtime, (int, float)) and runtime > 45


FORMAT_RULES: List[Dict[str, Any]] = [
    {"title": "Courts métrages", "predicate": _is_short_form},
    {"title": "Longs métrages", "predicate": _is_long_form},
    {"title": "Durée inconnue", "predicate": lambda item: item.get("runtime") in (None, "", 0)},
]


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
    extra_directors = [
        member.get("name")
        for member in crew
        if member.get("department") == "Directing" and member.get("name")
    ]
    directors.extend(extra_directors)
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
        "backdrop_url": _build_backdrop_url(movie.get("backdrop_path") or summary.get("backdrop_path")),
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


def _fallback_movie() -> Optional[Dict[str, Any]]:
    if not FALLBACK_QUEER_MOVIES:
        return None
    return random.choice(FALLBACK_QUEER_MOVIES)


def fetch_random_queer_movie() -> Optional[Dict[str, Any]]:
    client: Optional[TmdbClient]
    try:
        client = get_tmdb_client()
    except ValueError:
        return _fallback_movie()

    if not client:
        return _fallback_movie()

    try:
        with client:
            payload = sample_movie_by_keyword(
                client,
                "Queer",
                append_to_response="credits,external_ids",
            )
    except TmdbError:
        return _fallback_movie()

    normalized = normalize_movie_payload(payload)
    if normalized:
        if not normalized.get("cast"):
            summary = payload.get("summary", {}) or {}
            cast = summary.get("cast") or []
            normalized["cast"] = [person.get("name") for person in cast[:4] if person.get("name")]
        if normalized.get("directors") is None:
            normalized["directors"] = []
        return normalized

    return _fallback_movie()


def _build_backdrop_url(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return f"{BACKDROP_BASE_URL}{path}"


def _extract_watch_providers(details: Dict[str, Any]) -> Dict[str, Any]:
    providers = details.get("watch/providers") if isinstance(details.get("watch/providers"), dict) else {}
    results = providers.get("results", {}) if isinstance(providers, dict) else {}
    language = _normalize_language(getattr(settings, "TMDB_CONFIG", {}).get("LANGUAGE", "en-US"))
    region = (language.split("-")[-1]).upper() if "-" in language else None
    region_data = (
        results.get(region)
        if region
        else None
    ) or results.get("FR") or results.get("US") or (next(iter(results.values())) if results else None)

    if not region_data:
        return {"providers": [], "link": None}

    link = region_data.get("link")
    collected: List[Dict[str, Any]] = []
    for category in ("flatrate", "rent", "buy", "free", "ads"):
        entries = region_data.get(category) or []
        for entry in entries:
            name = entry.get("provider_name")
            if not name:
                continue
            collected.append({
                "name": name,
                "type": category,
                "logo_path": _build_poster_url(entry.get("logo_path")),
            })

    return {"providers": collected, "link": link}


def _extract_similar_titles(details: Dict[str, Any], limit: int = 6) -> List[Dict[str, Any]]:
    similar_payload = details.get("similar") or {}
    if not isinstance(similar_payload, dict):
        similar_payload = {}
    results = similar_payload.get("results") or []
    if not results:
        recommendations = details.get("recommendations") or {}
        if isinstance(recommendations, dict):
            results = recommendations.get("results") or []

    items: List[Dict[str, Any]] = []
    for entry in results:
        title = entry.get("title") or entry.get("name")
        tmdb_id = entry.get("id")
        if not (title and tmdb_id):
            continue
        release = entry.get("release_date") or entry.get("first_air_date") or ""
        release_year = release.split("-")[0] if release else None
        items.append(
            {
                "tmdb_id": tmdb_id,
                "title": title,
                "poster_url": _build_poster_url(entry.get("poster_path")),
                "release_year": release_year,
            }
        )
        if len(items) >= limit:
            break
    return items


def _extract_genres(details: Dict[str, Any]) -> List[str]:
    genres = details.get("genres")
    if not isinstance(genres, list):
        return []
    names = [genre.get("name") for genre in genres if isinstance(genre, dict) and genre.get("name")]
    return names


def _serialize_media_item(media_item) -> Dict[str, Any]:
    metadata = media_item.metadata or {}
    summary = metadata.get("summary") or {}
    details = metadata.get("details") or {}

    overview = details.get("overview") or summary.get("overview") or media_item.overview
    release_date = details.get("release_date") or summary.get("release_date")
    release_year = release_date.split("-")[0] if isinstance(release_date, str) and release_date else None

    rating = details.get("vote_average") or summary.get("vote_average")
    vote_count = details.get("vote_count") or summary.get("vote_count")

    runtime = details.get("runtime") or (summary.get("runtime") if isinstance(summary, dict) else None)

    watch_info = _extract_watch_providers(details)
    similar = _extract_similar_titles(details)
    genres = _extract_genres(details)

    credits = details.get("credits") or {}
    cast = credits.get("cast") or []
    directors = [
        person.get("name")
        for person in credits.get("crew") or []
        if person.get("job") == "Director" and person.get("name")
    ]

    if not directors:
        directors = [
            person.get("name")
            for person in credits.get("crew") or []
            if person.get("department") == "Directing" and person.get("name")
        ]

    def _dedupe(seq: Iterable[str]) -> List[str]:
        seen: set[str] = set()
        return [item for item in seq if not (item in seen or seen.add(item))]

    directors = _dedupe(directors)
    cast_names = _dedupe([person.get("name") for person in cast if person.get("name")])[:6]

    return {
        "id": media_item.id,
        "tmdb_id": media_item.tmdb_id,
        "title": media_item.title,
        "original_title": media_item.original_title if media_item.original_title != media_item.title else None,
        "overview": overview,
        "poster_url": media_item.poster_url or _build_poster_url(summary.get("poster_path")),
        "backdrop_url": media_item.backdrop_url or _build_backdrop_url(details.get("backdrop_path") or summary.get("backdrop_path")),
        "release_year": release_year,
        "rating": rating,
        "vote_count": vote_count,
        "genres": genres,
        "runtime": runtime,
        "cast": cast_names,
        "directors": directors,
        "watch": watch_info,
        "similar": similar,
        "media_type": media_item.media_type,
        "metadata": {
            "summary": summary,
            "details": details,
        },
    }


def _serialize_media_list(media_list: MediaList, *, title: str, theme_slug: str) -> Dict[str, Any]:
    items = [
        _serialize_media_item(item.media_item)
        for item in media_list.items.select_related("media_item").order_by("position")
    ]
    return {
        "theme": theme_slug,
        "slug": media_list.slug,
        "title": title,
        "items": items,
        "source_keyword": media_list.source_keyword.slug if media_list.source_keyword else None,
        "fallback": False,
    }


def _fallback_carousel(theme: Dict[str, str]) -> Dict[str, Any]:
    fallback_key = theme.get("fallback") or theme["slug"]
    payload = FALLBACK_THEME_LISTS.get(fallback_key, {"items": []})
    items = payload.get("items", [])
    normalized = [
        {
            "tmdb_id": item.get("tmdb_id"),
            "title": item.get("title"),
            "overview": item.get("overview"),
            "poster_url": item.get("poster_url"),
            "release_year": item.get("release_year"),
            "rating": item.get("rating"),
            "genres": item.get("genres", []),
            "cast": item.get("cast", []),
            "directors": item.get("directors", []),
            "watch": {"providers": [], "link": None},
            "similar": [],
            "media_type": "movie",
            "metadata": {},
        }
        for item in items
    ]
    theme_slug = theme["slug"]
    return {
        "theme": theme_slug,
        "slug": payload.get("slug") or theme_slug,
        "title": payload.get("title") or theme["title"],
        "items": normalized,
        "source_keyword": None,
        "fallback": True,
    }


def get_feed_themes() -> List[Dict[str, str]]:
    return FEED_THEMES


def build_feed_carousel(
    theme_slug: str,
    *,
    user,
    limit: int = 12,
    language: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    theme = next((entry for entry in FEED_THEMES if entry["slug"] == theme_slug), None)
    if not theme:
        return None

    try:
        tag = IdentityTag.objects.get(slug=theme_slug)
    except IdentityTag.DoesNotExist:
        return _fallback_carousel(theme)

    language = _normalize_language(language or getattr(settings, "TMDB_CONFIG", {}).get("LANGUAGE"))

    try:
        media_list = generate_media_list_for_identity(
            tag=tag,
            owner=user,
            limit=limit,
            include_adult=False,
            language=language,
            visibility=MediaList.VISIBILITY_UNLISTED,
            title=theme["title"],
            description=f"Sélection de films et séries autour de {theme['title'].lower()}",
        )
    except TmdbError:
        return _fallback_carousel(theme)

    return _serialize_media_list(media_list, title=theme["title"], theme_slug=theme_slug)


def build_feed_carousels(user, *, limit: int = 12, language: Optional[str] = None) -> List[Dict[str, Any]]:
    carousels: List[Dict[str, Any]] = []
    for theme in FEED_THEMES:
        data = build_feed_carousel(theme["slug"], user=user, limit=limit, language=language)
        if data:
            carousels.append(data)
    return carousels


def _item_key(item: Dict[str, Any]) -> str:
    return str(item.get("tmdb_id") or item.get("id") or item.get("title") or id(item))


def _build_sections(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    covered: set[str] = set()

    for rule in FORMAT_RULES:
        predicate = rule["predicate"]
        bucket = [item for item in items if predicate(item)]
        if bucket:
            sections.append({"title": rule["title"], "items": bucket})
            covered.update(_item_key(item) for item in bucket)

    for genre_map in GENRE_CATEGORY_MAP:
        match_set = {token.lower() for token in genre_map["match"]}
        bucket = [
            item
            for item in items
            if any((genre or "").lower() in match_set for genre in item.get("genres", []))
        ]
        if bucket:
            sections.append({"title": genre_map["title"], "items": bucket})
            covered.update(_item_key(item) for item in bucket)

    remaining = [item for item in items if _item_key(item) not in covered]
    if remaining:
        sections.append({"title": "Autres essentiels", "items": remaining})

    return sections


def _select_feature_item(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not items:
        return None

    def sort_key(item: Dict[str, Any]):
        rating = item.get("rating") or 0
        vote_count = item.get("vote_count") or 0
        return (rating, vote_count)

    return max(items, key=sort_key)


def _build_detail_payload(
    *,
    theme: Dict[str, str],
    items: List[Dict[str, Any]],
    fallback: bool,
    media_list: Optional[MediaList],
) -> Dict[str, Any]:
    feature = _select_feature_item(items)
    sections = _build_sections(items)

    return {
        "theme": theme["slug"],
        "title": theme["title"],
        "description": (
            media_list.source_keyword.description if media_list and media_list.source_keyword else None
        ) or theme.get("description") or "",
        "items_count": len(items),
        "feature": feature,
        "sections": sections,
        "fallback": fallback,
        "source_keyword": media_list.source_keyword.slug if media_list and media_list.source_keyword else None,
        "list_slug": media_list.slug if media_list else None,
    }


def build_theme_detail(
    theme_slug: str,
    *,
    user,
    limit: int = 36,
    language: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    theme = next((entry for entry in FEED_THEMES if entry["slug"] == theme_slug), None)
    if not theme:
        return None

    language = _normalize_language(language or getattr(settings, "TMDB_CONFIG", {}).get("LANGUAGE"))

    try:
        tag = IdentityTag.objects.get(slug=theme_slug)
    except IdentityTag.DoesNotExist:
        fallback = _fallback_carousel(theme)
        return _build_detail_payload(theme=theme, items=fallback["items"], fallback=True, media_list=None)

    try:
        media_list = generate_media_list_for_identity(
            tag=tag,
            owner=user,
            limit=limit,
            include_adult=False,
            language=language,
            visibility=MediaList.VISIBILITY_UNLISTED,
            title=theme["title"],
            description=f"Sélection de films et séries autour de {theme['title'].lower()}",
        )
    except TmdbError:
        fallback = _fallback_carousel(theme)
        return _build_detail_payload(theme=theme, items=fallback["items"], fallback=True, media_list=None)

    items = [
        _serialize_media_item(entry.media_item)
        for entry in media_list.items.select_related("media_item").order_by("position")
    ]

    return _build_detail_payload(theme=theme, items=items, fallback=False, media_list=media_list)
