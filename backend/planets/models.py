from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Planet(models.Model):
    """Member-crafted worlds representing identity constellations."""

    VISIBILITY_PUBLIC = "public"
    VISIBILITY_INVITE = "invite"
    VISIBILITY_PRIVATE = "private"
    VISIBILITY_CHOICES = (
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_INVITE, "Invite only"),
        (VISIBILITY_PRIVATE, "Private"),
    )

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    accent_color = models.CharField(max_length=7, default="#8B5CF6")
    cover_image = models.ImageField(upload_to="planets/covers/", blank=True, null=True)
    avatar = models.ImageField(upload_to="planets/avatars/", blank=True, null=True)

    visibility = models.CharField(
        max_length=16,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
    )
    is_featured = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planets_created",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="PlanetMembership",
        through_fields=("planet", "user"),
        related_name="planets",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if not self.name.strip():
            raise ValidationError({"name": "Planet name cannot be blank."})

    @property
    def has_custom_appearance(self) -> bool:
        return hasattr(self, "appearance")


class PlanetAppearance(models.Model):
    """Structured visual + emotional identity captured by the chatbot builder."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATING = "generating", "Generating"
        LIVE = "live", "Live"
        NEEDS_REGEN = "needs_regen", "Needs regeneration"
        ARCHIVED = "archived", "Archived"

    class SurfaceType(models.TextChoices):
        GAS = "gas", "Gas giant"
        ICE = "ice", "Ice"
        OCEANIC = "oceanic", "Oceanic"
        ROCKY = "rocky", "Rocky"
        METALLIC = "metallic", "Metallic"
        ORGANIC = "organic", "Organic"
        CRYSTALLINE = "crystalline", "Crystalline"
        HYBRID = "hybrid", "Hybrid"

    class RingStyle(models.TextChoices):
        NONE = "none", "None"
        SINGLE = "single", "Single"
        DOUBLE = "double", "Double"
        MULTIPLE = "multiple", "Multiple"
        FRAGMENTED = "fragmented", "Fragmented"
        HALO = "halo", "Halo"

    class AtmosphereStyle(models.TextChoices):
        NONE = "none", "None"
        AURORA = "aurora", "Aurora"
        NEBULA = "nebula", "Nebula"
        STORMY = "stormy", "Stormy"
        CALM = "calm", "Calm"
        GLOWING = "glowing", "Glowing"
        VAPORWAVE = "vaporwave", "Vaporwave"

    class OriginType(models.TextChoices):
        NATURAL = "natural", "Natural"
        CRAFTED = "crafted", "Crafted"
        RECLAIMED = "reclaimed", "Reclaimed"
        BIOENGINEERED = "bioengineered", "Bioengineered"
        RITUAL = "ritual", "Ritual"
        UNKNOWN = "unknown", "Unknown"

    class EmotionalTone(models.TextChoices):
        SANCTUARY = "sanctuary", "Sanctuary"
        REBELLIOUS = "rebellious", "Rebellious"
        JUBILANT = "jubilant", "Jubilant"
        REFLECTIVE = "reflective", "Reflective"
        FIERY = "fiery", "Fiery"
        TENDER = "tender", "Tender"
        ENIGMATIC = "enigmatic", "Enigmatic"
        CUSTOM = "custom", "Custom"

    planet = models.OneToOneField(
        Planet,
        on_delete=models.CASCADE,
        related_name="appearance",
        primary_key=True,
    )

    name = models.CharField(max_length=140)
    tagline = models.CharField(max_length=255, blank=True)
    motto = models.CharField(max_length=255, blank=True)

    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7, blank=True)
    palette = models.JSONField(blank=True, default=list)

    surface_type = models.CharField(
        max_length=16,
        choices=SurfaceType.choices,
        default=SurfaceType.ROCKY,
    )
    surface_descriptors = models.JSONField(blank=True, default=list)

    ring_style = models.CharField(
        max_length=16,
        choices=RingStyle.choices,
        default=RingStyle.NONE,
    )
    ring_descriptors = models.JSONField(blank=True, default=list)
    ring_color = models.CharField(max_length=7, blank=True)

    has_moons = models.BooleanField(default=False)
    moon_count = models.PositiveSmallIntegerField(blank=True, null=True)
    moon_descriptors = models.JSONField(blank=True, default=list)

    atmosphere_style = models.CharField(
        max_length=16,
        choices=AtmosphereStyle.choices,
        default=AtmosphereStyle.NONE,
    )
    atmosphere_descriptors = models.JSONField(blank=True, default=list)

    origin_type = models.CharField(
        max_length=16,
        choices=OriginType.choices,
        default=OriginType.NATURAL,
    )
    materials = models.JSONField(blank=True, default=list)

    emotional_tone = models.CharField(
        max_length=16,
        choices=EmotionalTone.choices,
        default=EmotionalTone.SANCTUARY,
    )
    emotional_custom_label = models.CharField(max_length=120, blank=True)

    accessibility_notes = models.TextField(blank=True)

    trigger_avoidance_tags = models.ManyToManyField(
        "accounts.TriggerTopic",
        blank=True,
        related_name="planet_appearances",
    )
    custom_trigger_warnings = models.JSONField(blank=True, default=list)

    hero_image = models.ImageField(upload_to="planets/hero_images/", blank=True, null=True)
    icon_image = models.ImageField(upload_to="planets/icons/", blank=True, null=True)

    hero_prompt = models.TextField(blank=True)
    icon_prompt = models.TextField(blank=True)
    generator_version = models.CharField(max_length=64, blank=True)

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["planet__name"]

    def __str__(self) -> str:
        return f"Appearance of {self.planet.name}"

    @property
    def is_ready(self) -> bool:
        return self.status == self.Status.LIVE and bool(self.hero_image and self.icon_image)

    def mark_regeneration_needed(self) -> None:
        self.status = self.Status.NEEDS_REGEN
        self.save(update_fields=["status", "updated_at"])


class PlanetBuilderSession(models.Model):
    """Persistent draft state for the planet builder chatbot."""

    planet = models.OneToOneField(
        Planet,
        on_delete=models.CASCADE,
        related_name="builder_session",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planet_builder_sessions",
    )
    step_index = models.PositiveSmallIntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)
    skipped_steps = models.JSONField(default=list, blank=True)
    confirmations = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Builder session for {self.planet.name}"

    def reset(self) -> None:
        self.step_index = 0
        self.attributes = {}
        self.skipped_steps = []
        self.confirmations = {}
        self.is_active = True
        self.save()


class PlanetMembership(models.Model):
    """Relationship between a planet and a member, with roles."""

    ROLE_OWNER = "owner"
    ROLE_STEWARD = "steward"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = (
        (ROLE_OWNER, "Owner"),
        (ROLE_STEWARD, "Steward"),
        (ROLE_MEMBER, "Member"),
    )

    planet = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name="membership_links")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planet_memberships",
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="planet_invitations_sent",
        blank=True,
        null=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    can_curate = models.BooleanField(default=False)

    class Meta:
        unique_together = ("planet", "user")
        ordering = ["planet__name", "user__username"]

    def __str__(self) -> str:
        return f"{self.user.username} @ {self.planet.slug}"

    def clean(self) -> None:
        super().clean()
        if self.role == self.ROLE_OWNER and self.invited_by and self.invited_by != self.user:
            raise ValidationError({"role": "Planet owners cannot be invited by someone else."})
