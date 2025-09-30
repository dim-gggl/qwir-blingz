"""Higher-level discovery helpers built on the TMDb client."""

import random
from typing import Any, Dict, Optional

from ..client import TmdbClient
from ..exceptions import TmdbNotFoundError

MAX_DISCOVER_PAGES = 500  # TMDb caps discover pagination at 500.


def resolve_keyword_id(
    client: TmdbClient,
    keyword_query: str,
    *,
    prefer_exact: bool = True,
) -> Optional[int]:
    """Resolve a human-readable keyword into a TMDb keyword ID.

    We attempt to find an exact, case-insensitive match first. If no exact match
    exists, the first result is returned as a best-effort fallback.
    """

    if not keyword_query:
        raise ValueError("keyword_query must not be empty")

    response = client.search_keyword(keyword_query)
    results = response.get("results", []) or []

    if not results:
        return None

    if prefer_exact:
        lowered = keyword_query.strip().lower()
        for match in results:
            if match.get("name", "").lower() == lowered:
                return match.get("id")

    # Fall back to the first result if available.
    return results[0].get("id")


def sample_movie_by_keyword(
    client: TmdbClient,
    keyword_query: str,
    *,
    include_adult: bool = False,
    language: Optional[str] = None,
    sort_by: str = "popularity.desc",
    append_to_response: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch a random movie for the provided keyword.

    Raises:
        TmdbNotFoundError: when the keyword cannot be resolved or no movies are
            returned by the discovery endpoint.

    Additional keyword arguments:
        append_to_response: optional comma separated list of extra sections to
            retrieve alongside the movie detail (e.g., 'credits,external_ids').
    """

    keyword_id = resolve_keyword_id(client, keyword_query)
    if not keyword_id:
        raise TmdbNotFoundError(f"No TMDb keyword found for '{keyword_query}'")

    discover_params: Dict[str, Any] = {
        "with_keywords": str(keyword_id),
        "include_adult": include_adult,
        "sort_by": sort_by,
        "page": 1,
    }

    payload = client.discover_movies(**discover_params)
    total_results = payload.get("total_results", 0)
    total_pages = payload.get("total_pages", 0)

    if not total_results:
        raise TmdbNotFoundError(
            f"No TMDb titles found for keyword '{keyword_query}' (id={keyword_id})"
        )

    capped_pages = min(total_pages or 1, MAX_DISCOVER_PAGES)
    target_page = 1
    if capped_pages > 1:
        target_page = random.randint(1, capped_pages)
        if target_page != 1:
            payload = client.discover_movies(**{**discover_params, "page": target_page})

    results = payload.get("results") or []
    if not results:
        raise TmdbNotFoundError(
            f"TMDb returned no results for keyword '{keyword_query}' (id={keyword_id})"
        )

    pick = random.choice(results)
    movie_id = pick.get("id")
    if not movie_id:
        raise TmdbNotFoundError(
            f"Selected TMDb entry is missing an id for keyword '{keyword_query}'"
        )

    details = client.get_movie_details(
        movie_id,
        language=language,
        append_to_response=append_to_response,
    )

    return {
        "keyword": keyword_query,
        "keyword_id": keyword_id,
        "page": target_page,
        "movie": details,
        "summary": pick,
    }
