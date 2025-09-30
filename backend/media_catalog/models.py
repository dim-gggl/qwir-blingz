from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class IdentityTag(models.Model):
    """Labels describing queer identities, themes, or communities."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    tmdb_keyword_id = models.PositiveIntegerField(blank=True, null=True)
    is_curated = models.BooleanField(default=True)
    accent_color = models.CharField(max_length=7, default="#F472B6")
    emoji = models.CharField(max_length=16, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="identity_tags_created",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class MediaItem(models.Model):
    """Representation of a TMDb-backed media entity."""

    MEDIA_TYPE_MOVIE = "movie"
    MEDIA_TYPE_TV = "tv"
    MEDIA_TYPE_CHOICES = (
        (MEDIA_TYPE_MOVIE, "Movie"),
        (MEDIA_TYPE_TV, "Series"),
    )

    tmdb_id = models.PositiveIntegerField(unique=True)
    media_type = models.CharField(max_length=16, choices=MEDIA_TYPE_CHOICES, default=MEDIA_TYPE_MOVIE)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(blank=True, null=True)
    poster_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    overview = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, default=dict)

    identity_tags = models.ManyToManyField(IdentityTag, related_name="media_items", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class MediaList(models.Model):
    """Curated or generated lists of media items."""

    VISIBILITY_PUBLIC = "public"
    VISIBILITY_UNLISTED = "unlisted"
    VISIBILITY_PRIVATE = "private"
    VISIBILITY_CHOICES = (
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_UNLISTED, "Unlisted"),
        (VISIBILITY_PRIVATE, "Private"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="media_lists/covers/", blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="media_lists",
    )

    visibility = models.CharField(max_length=16, choices=VISIBILITY_CHOICES, default=VISIBILITY_PUBLIC)
    is_dynamic = models.BooleanField(default=False)
    source_keyword = models.ForeignKey(
        IdentityTag,
        on_delete=models.SET_NULL,
        related_name="generated_lists",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class MediaListItem(models.Model):
    """Link media items to their list with ordering and annotations."""

    media_list = models.ForeignKey(MediaList, on_delete=models.CASCADE, related_name="items")
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name="list_entries")
    position = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="media_list_contributions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("media_list", "media_item")
        ordering = ["position", "-created_at"]

    def __str__(self) -> str:
        return f"{self.media_item} in {self.media_list}"
