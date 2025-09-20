from __future__ import annotations

from django.contrib import admin

from .models import Planet, PlanetAppearance, PlanetBuilderSession, PlanetMembership


class PlanetAppearanceInline(admin.StackedInline):
    model = PlanetAppearance
    can_delete = False
    extra = 0
    autocomplete_fields = ("trigger_avoidance_tags",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "tagline",
                    "motto",
                    "status",
                    "generator_version",
                )
            },
        ),
        (
            "Palette",
            {
                "fields": (
                    "primary_color",
                    "secondary_color",
                    "palette",
                )
            },
        ),
        (
            "Structure",
            {
                "fields": (
                    "surface_type",
                    "surface_descriptors",
                    "ring_style",
                    "ring_descriptors",
                    "ring_color",
                    "has_moons",
                    "moon_count",
                    "moon_descriptors",
                    "atmosphere_style",
                    "atmosphere_descriptors",
                )
            },
        ),
        (
            "Lore",
            {
                "fields": (
                    "origin_type",
                    "materials",
                    "emotional_tone",
                    "emotional_custom_label",
                    "accessibility_notes",
                    "trigger_avoidance_tags",
                    "custom_trigger_warnings",
                )
            },
        ),
        (
            "Assets",
            {
                "fields": (
                    "hero_image",
                    "icon_image",
                    "hero_prompt",
                    "icon_prompt",
                )
            },
        ),
    )


@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "visibility", "created_by", "is_featured", "created_at")
    search_fields = ("name", "slug", "tagline", "description")
    list_filter = ("visibility", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("created_by",)
    inlines = [PlanetAppearanceInline]


@admin.register(PlanetAppearance)
class PlanetAppearanceAdmin(admin.ModelAdmin):
    list_display = (
        "planet",
        "status",
        "surface_type",
        "origin_type",
        "emotional_tone",
        "updated_at",
    )
    list_filter = (
        "status",
        "surface_type",
        "origin_type",
        "emotional_tone",
    )
    search_fields = (
        "planet__name",
        "name",
        "motto",
        "tagline",
    )
    autocomplete_fields = (
        "planet",
        "trigger_avoidance_tags",
    )


@admin.register(PlanetBuilderSession)
class PlanetBuilderSessionAdmin(admin.ModelAdmin):
    list_display = ("planet", "user", "step_index", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("planet__name", "planet__slug", "user__username")
    autocomplete_fields = ("planet", "user")
    readonly_fields = ("attributes", "skipped_steps", "confirmations", "created_at", "updated_at")


@admin.register(PlanetMembership)
class PlanetMembershipAdmin(admin.ModelAdmin):
    list_display = ("planet", "user", "role", "can_curate", "joined_at")
    list_filter = ("role", "can_curate")
    search_fields = ("planet__name", "planet__slug", "user__username")
    autocomplete_fields = ("planet", "user", "invited_by")
