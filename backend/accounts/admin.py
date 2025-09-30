from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import TriggerTopic, User, UserTriggerPreference


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Community profile",
            {
                "fields": (
                    "full_name",
                    "display_full_name",
                    "gender_identity",
                    "display_gender_identity",
                    "pronouns",
                    "birth_date",
                    "display_birth_date",
                    "display_email",
                    "bio",
                    "avatar",
                )
            },
        ),
    )
    list_display = (
        "username",
        "email",
        "display_email",
        "display_full_name",
        "display_gender_identity",
        "display_birth_date",
        "is_active",
        "is_staff",
    )
    search_fields = ("username", "email", "full_name", "gender_identity", "pronouns")


@admin.register(TriggerTopic)
class TriggerTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_by", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(UserTriggerPreference)
class UserTriggerPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "custom_label", "created_at")
    search_fields = ("user__username", "custom_label", "topic__name")
    autocomplete_fields = ("user", "topic")
