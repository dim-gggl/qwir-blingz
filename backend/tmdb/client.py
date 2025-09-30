"""Low-level TMDb client utilities."""

import logging
from typing import Any, Dict, Optional

import httpx

from config.settings import TMDB_CONFIG as settings

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

    

    def __init__(
        self,
        api_key: str = settings["API_KEY"],
        *,
        base_url: str = settings["DEFAULT_BASE_URL"],
        timeout: float = settings["TIMEOUT"],
        default_language: str = settings["LANGUAGE"],
        client: Optional[httpx.Client] = None,
    ) -> None:
        if not api_key:
            raise ValueError("TMDb API key must be provided")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_language = default_language

        # Detect if this is a Bearer token (JWT format) or standard API key
        self._is_bearer_token = api_key.startswith("eyJ") and api_key.count(".") >= 2

        headers = {}
        if self._is_bearer_token:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["accept"] = "application/json"

        self._client = client or httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=headers
        )
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
        query = {"language": self.default_language}

        # Only add api_key to query params if we're not using Bearer token
        if not self._is_bearer_token:
            query["api_key"] = self.api_key

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
