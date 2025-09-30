from datetime import date
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


class User(AbstractUser):
    """Custom user model with granular visibility controls."""

    email = models.EmailField("email address", blank=True)
    display_email = models.BooleanField(default=False)

    full_name = models.CharField(max_length=255, blank=True)
    display_full_name = models.BooleanField(default=False)

    gender_identity = models.CharField(max_length=255, blank=True)
    display_gender_identity = models.BooleanField(default=False)

    pronouns = models.CharField(max_length=64, blank=True)

    birth_date = models.DateField(blank=True, null=True)
    display_birth_date = models.BooleanField(default=False)

    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        super().clean()
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError({"birth_date": "Birth date cannot be in the future."})

    @property
    def safe_email(self) -> str | None:
        return self.email if self.display_email else None

    @property
    def safe_full_name(self) -> str | None:
        return self.full_name if self.display_full_name else None

    @property
    def safe_birth_date(self) -> date | None:
        return self.birth_date if self.display_birth_date else None

    @property
    def safe_gender_identity(self) -> str | None:
        return self.gender_identity if self.display_gender_identity else None

    @property
    def curated_trigger_topics(self) -> QuerySet["TriggerTopic"]:
        """Convenience accessor for curated trigger topics."""

        return TriggerTopic.objects.filter(user_preferences__user=self)


class TriggerTopic(models.Model):
    """Curated list of trigger topics that users can opt out of seeing."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_trigger_topics",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserTriggerPreference(models.Model):
    """User-specified trigger warnings, supporting curated or custom topics."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trigger_preferences",
    )
    topic = models.ForeignKey(
        TriggerTopic,
        on_delete=models.CASCADE,
        related_name="user_preferences",
        blank=True,
        null=True,
    )
    custom_label = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "topic", "custom_label")
        ordering = ["user", "topic__name", "custom_label"]

    def clean(self) -> None:
        super().clean()
        if not self.topic and not self.custom_label:
            raise ValidationError("Either a curated topic or a custom label must be provided.")

    def __str__(self) -> str:
        if self.topic:
            return f"{self.user.username} – {self.topic.name}"
        return f"{self.user.username} – {self.custom_label}"
