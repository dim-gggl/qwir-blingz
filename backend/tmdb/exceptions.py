"""Custom exceptions for TMDb interactions."""

from __future__ import annotations


class TmdbError(RuntimeError):
    """Base error for TMDb client issues."""


class TmdbAuthorizationError(TmdbError):
    """Raised when TMDb rejects our credentials."""


class TmdbRateLimitError(TmdbError):
    """Raised when TMDb throttles requests."""


class TmdbNotFoundError(TmdbError):
    """Raised when a requested resource cannot be found."""
