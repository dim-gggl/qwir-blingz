from __future__ import annotations

from django.contrib import admin

from .models import IdentityTag, MediaItem, MediaList, MediaListItem


@admin.register(IdentityTag)
class IdentityTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "tmdb_keyword_id", "is_curated", "created_at")
    search_fields = ("name", "slug", "description")
    list_filter = ("is_curated",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "tmdb_id", "release_date")
    search_fields = ("title", "original_title", "tmdb_id")
    list_filter = ("media_type", "identity_tags")
    autocomplete_fields = ("identity_tags",)


class MediaListItemInline(admin.TabularInline):
    model = MediaListItem
    extra = 0
    autocomplete_fields = ("media_item", "added_by")


@admin.register(MediaList)
class MediaListAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "visibility", "is_dynamic", "created_at")
    search_fields = ("title", "description", "owner__username")
    list_filter = ("visibility", "is_dynamic")
    autocomplete_fields = ("owner", "source_keyword")
    inlines = [MediaListItemInline]


@admin.register(MediaListItem)
class MediaListItemAdmin(admin.ModelAdmin):
    list_display = ("media_list", "media_item", "position", "added_by", "created_at")
    search_fields = (
        "media_list__title",
        "media_item__title",
        "media_item__tmdb_id",
        "added_by__username",
    )
    list_filter = ("media_list",)
    autocomplete_fields = ("media_list", "media_item", "added_by")
