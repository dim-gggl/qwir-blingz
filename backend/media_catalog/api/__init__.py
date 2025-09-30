"""API wiring for the media_catalog app."""

from .views import MediaListViewSet, IdentityTagViewSet

__all__ = ["MediaListViewSet", "IdentityTagViewSet"]
