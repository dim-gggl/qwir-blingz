from __future__ import annotations

from django.db import migrations

ADDITIONAL_FEED_TAGS = [
    {
        "name": "Bi",
        "slug": "bisexual",
        "description": "Identités bisexuelles, pansexuelles et plurisexuelles à l'écran.",
        "emoji": "💗",
    },
    {
        "name": "Pan",
        "slug": "pansexual",
        "description": "Narrations pansexuelles et polyromantiques, amours sans frontières.",
        "emoji": "🌺",
    },
    {
        "name": "Joies handies",
        "slug": "disability-joy",
        "description": "Récits handis, mad pride, neurodivergence et fierté crip.",
        "emoji": "♿",
    },
    {
        "name": "LGBTQ+ racisé·es",
        "slug": "bipoc-lgbtq",
        "description": "Expériences LGBTQ+ racisées, décoloniales et intersectionnelles.",
        "emoji": "🌍",
    },
]


def seed_additional_tags(apps, schema_editor):
    IdentityTag = apps.get_model("media_catalog", "IdentityTag")
    for entry in ADDITIONAL_FEED_TAGS:
        IdentityTag.objects.get_or_create(
            slug=entry["slug"],
            defaults={
                "name": entry["name"],
                "description": entry["description"],
                "emoji": entry["emoji"],
                "is_curated": True,
            },
        )


def purge_additional_tags(apps, schema_editor):
    IdentityTag = apps.get_model("media_catalog", "IdentityTag")
    IdentityTag.objects.filter(slug__in=[entry["slug"] for entry in ADDITIONAL_FEED_TAGS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("media_catalog", "0002_seed_feed_identity_tags"),
    ]

    operations = [
        migrations.RunPython(seed_additional_tags, purge_additional_tags),
    ]