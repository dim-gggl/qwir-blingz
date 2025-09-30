from __future__ import annotations

from django.db import migrations

# Mapping des slugs vers les IDs de mots-clés TMDb basé sur les expérimentations
TMDB_KEYWORD_MAPPING = {
    # Trans identities
    "trans-joy": [
        265451,  # trans
        343076,  # trans-love
        254152,  # trans-activism
        268076,  # trans-rights
        335948,  # trans rights
        274776,  # transidentity
        14702,   # transgender
        290527,  # transgender
    ],

    # Lesbian
    "lesbian-love": [
        264386,  # lesbian
        308586,  # lesbians
        315385,  # lesbian_love
        319872,  # lesbian_romance
        9833,    # lesbian-relationship
        15136,   # female-homosexuality
        305694,  # lesbian-history
    ],

    # Gay
    "gay-celebration": [
        258533,  # gay-theme
        10180,   # male-homosexuality
        275157,  # homosexuality
        173672,  # gay-liberation
        264411,  # gay-rights
        241179,  # gay-history
        259285,  # gay-artist
    ],

    # Queer
    "queer-joy": [
        250606,  # queer
        321567,  # queer-joy
        333327,  # queer-friends
        333766,  # queer-romance
        332049,  # queer-love
        312912,  # queer-cast
        300642,  # queer-cinema
    ],

    # LGBTQIA+
    "lgbt-history": [
        158718,  # lgbt
        346871,  # lgbtq
        348563,  # lgbtq+
        275749,  # lgbt-activism
        313433,  # lgbt-history
        280179,  # lgbt-rights
        156501,  # lgbt pride
        267488,  # lgbt chosen-family
    ],

    # Non-binary
    "non-binary": [
        252909,  # non-binary
        266529,  # genderqueer
        281283,  # genderfluid
        210039,  # gender-identity
        34221,   # gender-roles
        312910,  # trans-non-binary
    ],

    # Gender studies
    "gender-studies": [
        246413,  # gender-studies
        34214,   # gender
        210039,  # gender-identity
        234700,  # gender-transition
        11402,   # androgyny
    ],

    # Radical feminism
    "radical-feminism": [
        309966,  # radical-feminism
        2383,    # feminism
        11718,   # feminist
        301659,  # feminist-movement
        293179,  # global-feminism
        228965,  # intersectionality
    ],

    # Intersex
    "intersex": [
        240109,  # intersex
        257264,  # intersex-child
        9331,    # intersexuality
        273188,  # intersex gender-affirmation surgery
    ],

    # Asexual
    "asexual": [
        329977,  # asexual
        247099,  # asexuality
        329976,  # asex aromantic
        322171,  # aromantic-asexual
    ],

    # Sex work
    "tds-sex-work": [
        271159,  # tds sex-work
        13059,   # prostitution/sex-worker
        245541,  # sexworkers
        226543,  # sex_work
        190178,  # sex_worker
        163791,  # escort-girl
    ],

    # Bisexual
    "bisexual": [
        329968,  # bisexual
        168812,  # bisexual-man
        287417,  # bisexual-woman
        3183,    # bisexuality
    ],

    # Pansexual
    "pansexual": [
        262765,  # pansexual
        155870,  # polyamory
    ],

    # Disability/Handis (pas spécifiquement dans les expérimentations, using general terms)
    "disability-joy": [
        # Ces IDs seraient à compléter avec des recherches TMDb spécifiques
        # Pour l'instant on utilise les fallbacks
    ],

    # BIPOC LGBTQ+
    "bipoc-lgbtq": [
        316515,  # arab-lgbt
        195624,  # black-lgbt
        272309,  # black
        291081,  # black-woman
        233840,  # black-lives-matter
        11550,   # black-activist
    ],
}


def map_tmdb_keywords(apps, schema_editor):
    """Map TMDb keyword IDs to existing IdentityTags"""
    IdentityTag = apps.get_model("media_catalog", "IdentityTag")

    for slug, keyword_ids in TMDB_KEYWORD_MAPPING.items():
        try:
            tag = IdentityTag.objects.get(slug=slug)
            # Store the primary keyword ID and optionally additional ones
            if keyword_ids:
                tag.tmdb_keyword_id = keyword_ids[0]  # Primary keyword
                tag.save()
                print(f"Mapped {slug} to TMDb keyword ID: {keyword_ids[0]}")
        except IdentityTag.DoesNotExist:
            print(f"Tag with slug '{slug}' not found, skipping...")


def unmap_tmdb_keywords(apps, schema_editor):
    """Remove TMDb keyword IDs from IdentityTags"""
    IdentityTag = apps.get_model("media_catalog", "IdentityTag")

    for slug in TMDB_KEYWORD_MAPPING.keys():
        try:
            tag = IdentityTag.objects.get(slug=slug)
            tag.tmdb_keyword_id = None
            tag.save()
        except IdentityTag.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("media_catalog", "0003_add_additional_feed_tags"),
    ]

    operations = [
        migrations.RunPython(map_tmdb_keywords, unmap_tmdb_keywords),
    ]