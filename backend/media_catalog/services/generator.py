"""Media catalog services for TMDb-powered queer film discovery."""

import logging
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Sequence

from django.db import transaction
from django.utils.text import slugify

from tmdb import TmdbClient, TmdbError, TmdbNotFoundError, get_tmdb_client
from tmdb.services import resolve_keyword_id
from tmdb.keywords import get_primary_keyword_for_theme, get_keywords_for_theme

from media_catalog.models import IdentityTag, MediaItem, MediaList, MediaListItem

LOGGER = logging.getLogger(__name__)

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w780"
DEFAULT_APPEND = "credits,external_ids,keywords,release_dates,watch/providers,similar,recommendations"


@dataclass(slots=True)
class MoviePayload:
    """Normalized movie data coalesced from TMDb summary + detail calls."""

    tmdb_id: int
    title: str
    original_title: Optional[str]
    overview: str
    release_date: Optional[date]
    poster_url: Optional[str]
    backdrop_url: Optional[str]
    media_type: str
    metadata: Dict[str, object]


def _build_image_url(path: Optional[str], base: str) -> Optional[str]:
    if not path:
        return None
    return f"{base}{path}" if not base.endswith("/") else f"{base[:-1]}{path}"


def _normalize_movie(summary: Dict[str, object], details: Dict[str, object]) -> Optional[MoviePayload]:
    tmdb_id = int(details.get("id") or summary.get("id") or 0)
    if not tmdb_id:
        return None

    title = (details.get("title") or summary.get("title") or "").strip()
    if not title:
        return None

    original_title = details.get("original_title") or summary.get("original_title") or None
    if original_title == title:
        original_title = None

    overview = (details.get("overview") or summary.get("overview") or "").strip()

    release_date_str = details.get("release_date") or summary.get("release_date")
    parsed_date: Optional[date] = None
    if isinstance(release_date_str, str) and release_date_str:
        try:
            parsed_date = date.fromisoformat(release_date_str)
        except ValueError:
            LOGGER.debug("Unable to parse release date '%s' for TMDb id %s", release_date_str, tmdb_id)

    poster_path = details.get("poster_path") or summary.get("poster_path")
    backdrop_path = details.get("backdrop_path") or summary.get("backdrop_path")

    metadata = {
        "summary": summary,
        "details": details,
    }

    return MoviePayload(
        tmdb_id=tmdb_id,
        title=title,
        original_title=original_title,
        overview=overview,
        release_date=parsed_date,
        poster_url=_build_image_url(poster_path, POSTER_BASE_URL),
        backdrop_url=_build_image_url(backdrop_path, BACKDROP_BASE_URL),
        media_type=MediaItem.MEDIA_TYPE_MOVIE,
        metadata=metadata,
    )


def _ensure_keyword_id(tag: IdentityTag, client: TmdbClient) -> int:
    # First try to use our pre-mapped keyword from experiments
    if tag.tmdb_keyword_id:
        return tag.tmdb_keyword_id

    # Try to get keyword ID from our experimental mappings
    experimental_keyword_id = get_primary_keyword_for_theme(tag.slug)
    if experimental_keyword_id:
        LOGGER.info("Using experimental keyword ID %s for tag '%s'", experimental_keyword_id, tag.name)
        tag.tmdb_keyword_id = experimental_keyword_id
        tag.save(update_fields=["tmdb_keyword_id", "updated_at"])
        return experimental_keyword_id

    # Fallback to dynamic keyword resolution
    keyword_id = resolve_keyword_id(client, tag.name)
    if not keyword_id:
        raise TmdbNotFoundError(f"TMDb keyword for '{tag.name}' could not be resolved")

    tag.tmdb_keyword_id = keyword_id
    tag.save(update_fields=["tmdb_keyword_id", "updated_at"])
    return keyword_id


def _discover_movies(
    client: TmdbClient,
    *,
    keyword_id: int,
    limit: int,
    include_adult: bool,
    language: Optional[str],
    theme_slug: Optional[str] = None,
) -> Sequence[Dict[str, object]]:
    collected: List[Dict[str, object]] = []
    seen: set[int] = set()
    page = 1

    # Use multiple keywords from experiments if available for better results
    keyword_filter = str(keyword_id)
    if theme_slug:
        all_keywords = get_keywords_for_theme(theme_slug)
        if all_keywords and len(all_keywords) > 1:
            # Use up to 5 keywords (TMDb API limit) for better discovery
            keyword_filter = "|".join(str(k) for k in all_keywords[:5])
            LOGGER.info("Using multiple keywords for %s: %s", theme_slug, keyword_filter)

    while len(collected) < limit:
        params = {
            "with_keywords": keyword_filter,
            "include_adult": include_adult,
            "page": page,
            "sort_by": "popularity.desc",  # Get popular movies first
        }
        if language:
            params["language"] = language

        payload = client.discover_movies(**params)
        results = payload.get("results") or []

        for result in results:
            movie_id = result.get("id")
            if not movie_id or movie_id in seen:
                continue
            collected.append(result)
            seen.add(movie_id)
            if len(collected) >= limit:
                break

        total_pages = payload.get("total_pages") or 0
        if page >= total_pages or not results:
            break
        page += 1

    return collected


def _fetch_movie_details(
    client: TmdbClient,
    movie_ids: Iterable[int],
    *,
    append_to_response: Optional[str],
) -> Dict[int, Dict[str, object]]:
    details: Dict[int, Dict[str, object]] = {}
    for movie_id in movie_ids:
        details[movie_id] = client.get_movie_details(
            movie_id,
            append_to_response=append_to_response,
        )
    return details


@transaction.atomic
def generate_media_list_for_identity(
    *,
    tag: IdentityTag,
    owner: Any,
    limit: int = 12,
    include_adult: bool = False,
    language: Optional[str] = None,
    visibility: str = MediaList.VISIBILITY_PUBLIC,
    title: Optional[str] = None,
    description: Optional[str] = None,
    append_to_response: str = DEFAULT_APPEND,
    client: Optional[TmdbClient] = None,
) -> MediaList:
    """Generate or refresh a media list for the provided identity tag."""

    if limit <= 0:
        raise ValueError("limit must be positive")

    provided_client = client is not None
    client = client or get_tmdb_client()
    if client is None:
        raise TmdbError("TMDb client could not be initialized")

    context = client if not provided_client else nullcontext(client)
    with context:
        keyword_id = _ensure_keyword_id(tag, client)
        summaries = _discover_movies(
            client,
            keyword_id=keyword_id,
            limit=limit,
            include_adult=include_adult,
            language=language,
            theme_slug=tag.slug,
        )

        if not summaries:
            raise TmdbNotFoundError(
                f"TMDb discovery returned no results for keyword '{tag.name}' (id={keyword_id})"
            )

        movie_ids = [int(entry["id"]) for entry in summaries if entry.get("id")]
        detail_map = _fetch_movie_details(client, movie_ids, append_to_response=append_to_response)

    normalized: List[MoviePayload] = []
    for summary in summaries:
        movie_id = int(summary.get("id") or 0)
        detail = detail_map.get(movie_id, {})
        payload = _normalize_movie(summary, detail)
        if payload:
            normalized.append(payload)

    if not normalized:
        raise TmdbError("No valid TMDb entries could be normalized into media items")

    media_items: List[MediaItem] = []
    for payload in normalized:
        defaults = {
            "media_type": payload.media_type,
            "title": payload.title,
            "original_title": payload.original_title or payload.title,
            "release_date": payload.release_date,
            "poster_url": payload.poster_url or "",
            "backdrop_url": payload.backdrop_url or "",
            "overview": payload.overview,
            "metadata": payload.metadata,
        }
        media_item, _ = MediaItem.objects.update_or_create(
            tmdb_id=payload.tmdb_id,
            defaults=defaults,
        )
        media_item.identity_tags.add(tag)
        media_items.append(media_item)

    list_title = title or f"{tag.name} Spotlight"
    slug = slugify(f"{tag.slug}-spotlight-{tag.pk}")

    media_list, created = MediaList.objects.get_or_create(
        slug=slug,
        defaults={
            "title": list_title,
            "description": description or f"Films exploring {tag.name} journeys",
            "owner": owner,
            "visibility": visibility,
            "is_dynamic": True,
            "source_keyword": tag,
        },
    )

    updates: Dict[str, object] = {}
    if media_list.title != list_title:
        updates["title"] = list_title
    if description and media_list.description != description:
        updates["description"] = description
    if media_list.visibility != visibility:
        updates["visibility"] = visibility
    if media_list.source_keyword_id != tag.id:
        updates["source_keyword"] = tag
    if not media_list.is_dynamic:
        updates["is_dynamic"] = True

    if updates:
        for field, value in updates.items():
            setattr(media_list, field, value)
        media_list.save(update_fields=list(updates.keys()) + ["updated_at"])

    existing_items = {
        item.media_item_id: item for item in media_list.items.select_related("media_item")
    }

    desired_ids = [item.id for item in media_items]
    for obsolete_id, list_item in list(existing_items.items()):
        if obsolete_id not in desired_ids:
            list_item.delete()
            existing_items.pop(obsolete_id, None)

    for index, media_item in enumerate(media_items, start=1):
        list_item = existing_items.get(media_item.id)
        if list_item:
            if list_item.position != index:
                list_item.position = index
                list_item.save(update_fields=["position"])
            continue
        MediaListItem.objects.create(
            media_list=media_list,
            media_item=media_item,
            position=index,
        )

    media_list.refresh_from_db()
    return media_list
