"""Low-level TMDb client utilities."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    TmdbAuthorizationError,
    TmdbError,
    TmdbNotFoundError,
    TmdbRateLimitError,
)

LOGGER = logging.getLogger(__name__)


class TmdbClient:
    """Synchronous TMDb API client.

    Designed to be instantiated once per request or worker and reused for
    multiple API calls. The client injects the API key, default language, and
    timeout values for each call while providing convenience wrappers for the
    endpoints we need.
    """

    DEFAULT_BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        default_language: str = "en-US",
        client: Optional[httpx.Client] = None,
    ) -> None:
        if not api_key:
            raise ValueError("TMDb API key must be provided")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_language = default_language
        self._client = client or httpx.Client(base_url=self.base_url, timeout=self.timeout)
        self._owns_client = client is None

    # Context manager helpers so callers can use `with TmdbClient(...)` when needed.
    def __enter__(self) -> "TmdbClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:  # type: ignore[override]
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    # ---- HTTP helpers -------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        query = {
            "api_key": self.api_key,
            "language": self.default_language,
        }
        if params:
            query.update({key: value for key, value in params.items() if value is not None})

        try:
            response = self._client.request(method, path, params=query)
        except httpx.TimeoutException as exc:
            raise TmdbError("TMDb request timed out") from exc
        except httpx.RequestError as exc:
            raise TmdbError(f"TMDb request failed: {exc}") from exc

        if response.status_code == 401:
            raise TmdbAuthorizationError("TMDb rejected our API key")
        if response.status_code == 404:
            raise TmdbNotFoundError("TMDb resource not found")
        if response.status_code == 429:
            raise TmdbRateLimitError("TMDb rate limit exceeded")
        if response.status_code >= 400:
            raise TmdbError(
                f"TMDb request failed ({response.status_code}): {response.text}"
            )

        payload = response.json()
        LOGGER.debug("TMDb %s %s -> %s", method.upper(), path, response.status_code)
        return payload

    # ---- Public endpoint wrappers ------------------------------------
    def search_keyword(
        self,
        query: str,
        *,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for a keyword (e.g., Queer, Trans) by text."""

        if not query:
            raise ValueError("Query must not be empty")

        return self._request(
            "GET",
            "/search/keyword",
            params={"query": query, "page": page},
        )

    def discover_movies(self, **params: Any) -> Dict[str, Any]:
        """Call `/discover/movie` with the provided parameters."""

        return self._request("GET", "/discover/movie", params=params)

    def get_movie_details(
        self,
        movie_id: int,
        *,
        language: Optional[str] = None,
        append_to_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve a detailed movie payload."""

        if not movie_id:
            raise ValueError("movie_id must be provided")

        params: Dict[str, Any] = {}
        if language:
            params["language"] = language
        if append_to_response:
            params["append_to_response"] = append_to_response

        return self._request("GET", f"/movie/{movie_id}", params=params)

    def get_configuration(self) -> Dict[str, Any]:
        """Fetch TMDb API configuration (useful for image base URLs)."""

        return self._request("GET", "/configuration")
