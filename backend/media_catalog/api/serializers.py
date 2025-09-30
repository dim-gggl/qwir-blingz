"""Serializers for media catalog API endpoints."""

from typing import Optional
from rest_framework import serializers

from media_catalog.models import IdentityTag, MediaItem, MediaList, MediaListItem


class IdentityTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityTag
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "tmdb_keyword_id",
            "is_curated",
            "accent_color",
            "emoji",
        )


class MediaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaItem
        fields = (
            "id",
            "tmdb_id",
            "media_type",
            "title",
            "original_title",
            "overview",
            "release_date",
            "poster_url",
            "backdrop_url",
            "metadata",
        )


class MediaListItemSerializer(serializers.ModelSerializer):
    media_item = MediaItemSerializer(read_only=True)

    class Meta:
        model = MediaListItem
        fields = (
            "id",
            "position",
            "notes",
            "media_item",
        )


class MediaListSummarySerializer(serializers.ModelSerializer):
    source_keyword = IdentityTagSerializer(read_only=True)
    item_count = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaList
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "visibility",
            "is_dynamic",
            "source_keyword",
            "item_count",
            "share_url",
            "updated_at",
        )

    def get_item_count(self, obj: MediaList) -> int:
        return getattr(obj, "item_count", None) or obj.items.count()

    def get_share_url(self, obj: MediaList) -> Optional[str]:
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(f"/lists/{obj.slug}/")


class MediaListDetailSerializer(MediaListSummarySerializer):
    items = MediaListItemSerializer(source="items.all", many=True, read_only=True)

    class Meta(MediaListSummarySerializer.Meta):
        fields = MediaListSummarySerializer.Meta.fields + ("items",)


class MediaListGenerateSerializer(serializers.Serializer):
    identity_tag = serializers.PrimaryKeyRelatedField(queryset=IdentityTag.objects.all())
    limit = serializers.IntegerField(min_value=1, max_value=40, default=12)
    include_adult = serializers.BooleanField(default=False)
    language = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=MediaList.VISIBILITY_CHOICES,
        default=MediaList.VISIBILITY_PUBLIC,
    )
    title = serializers.CharField(required=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_language(self, value: str) -> Optional[str]:
        return value or None


class MediaListUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaList
        fields = (
            "title",
            "description",
            "visibility",
        )
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "visibility": {"required": False},
        }
