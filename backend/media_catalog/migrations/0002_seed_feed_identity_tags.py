from __future__ import annotations

from django.db import migrations

FEED_TAGS = [
    {
        "name": "Transidentités",
        "slug": "trans-joy",
        "description": "Films et séries centrés sur les expériences et les joies trans.",
        "emoji": "🌀",
    },
    {
        "name": "Lesbiennes",
        "slug": "lesbian-love",
        "description": "Histoires lesbiennes, romances, drames, docs et plus.",
        "emoji": "🌸",
    },
    {
        "name": "Gays",
        "slug": "gay-celebration",
        "description": "Créations gays : pride, mémoire, fêtes, luttes et amours.",
        "emoji": "🌈",
    },
    {
        "name": "Queers",
        "slug": "queer-joy",
        "description": "Panorama queer : joyeuses galaxies, club kids, ballrooms, résistance.",
        "emoji": "✨",
    },
    {
        "name": "LGBTQIA+",
        "slug": "lgbt-history",
        "description": "Archives et imaginaires LGBTQIA+ intergénérationnels.",
        "emoji": "🪐",
    },
    {
        "name": "Non-binaire",
        "slug": "non-binary",
        "description": "Identités non-binaires, fluides et genderqueer à l’écran.",
        "emoji": "🌗",
    },
    {
        "name": "Théories du Genre",
        "slug": "gender-studies",
        "description": "Essais, docs et fictions qui bousculent les cadres du genre.",
        "emoji": "📚",
    },
    {
        "name": "Féminisme radical",
        "slug": "radical-feminism",
        "description": "Héritages et combats transféministes décoloniaux.",
        "emoji": "🔥",
    },
    {
        "name": "Intersex",
        "slug": "intersex",
        "description": "Récits intersexes : lutte, douceur et autodétermination.",
        "emoji": "💫",
    },
    {
        "name": "Asexuel",
        "slug": "asexual",
        "description": "Narrations ace et aromantiques, des contes aux docs.",
        "emoji": "💜",
    },
    {
        "name": "Travail du sexe",
        "slug": "tds-sex-work",
        "description": "Travail du sexe, mutual aid, luttes anti-répression.",
        "emoji": "💋",
    },
]


def seed_tags(apps, schema_editor):
    IdentityTag = apps.get_model("media_catalog", "IdentityTag")
    for entry in FEED_TAGS:
        IdentityTag.objects.get_or_create(
            slug=entry["slug"],
            defaults={
                "name": entry["name"],
                "description": entry["description"],
                "emoji": entry["emoji"],
                "is_curated": True,
            },
        )


def purge_tags(apps, schema_editor):
    IdentityTag = apps.get_model("media_catalog", "IdentityTag")
    IdentityTag.objects.filter(slug__in=[entry["slug"] for entry in FEED_TAGS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("media_catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_tags, purge_tags),
    ]
