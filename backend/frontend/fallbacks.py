"""Curated fallback data for welcome page and feed surfaces."""

from typing import Dict, Sequence

FALLBACK_QUEER_MOVIES: Sequence[dict] = (
    {
        "title": "The Watermelon Woman",
        "original_title": None,
        "overview": (
            "Cheryl, a young Black lesbian, embarks on a documentary quest to uncover the legacy of a forgotten 1930s film star while navigating her own love story."
        ),
        "poster_url": None,
        "release_year": "1996",
        "origin_country": "United States",
        "original_language": "en",
        "cast": ["Cheryl Dunye", "Guinevere Turner", "Valarie Walker", "Cheryl Clarke"],
        "rating": 7.0,
        "vote_count": 81,
        "directors": ["Cheryl Dunye"],
        "tmdb_id": 31609,
        "tmdb_url": "https://www.themoviedb.org/movie/31609",
        "imdb_id": "tt0118125",
        "imdb_url": "https://www.imdb.com/title/tt0118125/",
    },
    {
        "title": "Rafiki",
        "original_title": None,
        "overview": (
            "When love blooms between two young women whose families are political rivals in Nairobi, they must choose between their hearts and the demands of their community."
        ),
        "poster_url": None,
        "release_year": "2018",
        "origin_country": "Kenya",
        "original_language": "sw",
        "cast": ["Samantha Mugatsia", "Sheila Munyiva", "Jimmi Gathu", "Nini Wacera"],
        "rating": 7.1,
        "vote_count": 143,
        "directors": ["Wanuri Kahiu"],
        "tmdb_id": 497698,
        "tmdb_url": "https://www.themoviedb.org/movie/497698",
        "imdb_id": "tt8286894",
        "imdb_url": "https://www.imdb.com/title/tt8286894/",
    },
    {
        "title": "Sissako's Saturn",
        "original_title": None,
        "overview": (
            "A dreamy collective of queer disabled artists crash-land on a neon planet and craft a chosen family while remixing Afrofuturist folklore."
        ),
        "poster_url": None,
        "release_year": "2015",
        "origin_country": "Mali",
        "original_language": "fr",
        "cast": ["Kadiatou Diabaté", "Issa Traoré", "Mariam Koné"],
        "rating": 7.8,
        "vote_count": 54,
        "directors": ["Aïcha Traoré"],
        "tmdb_id": None,
        "tmdb_url": None,
        "imdb_id": None,
        "imdb_url": None,
    },
)


FALLBACK_THEME_LISTS: Dict[str, dict] = {
    "transidentites": {
        "title": "Transidentités",
        "items": [
            {
                "tmdb_id": 497698,
                "title": "Rafiki",
                "poster_url": None,
                "overview": "Deux adolescentes queer défient les règles d'une Nairobi conservatrice pour vivre leur amour.",
                "release_year": "2018",
                "origin_country": "Kenya",
                "rating": 7.1,
            },
            {
                "tmdb_id": 762504,
                "title": "No Ordinary Man",
                "poster_url": None,
                "overview": "Le parcours de Billy Tipton revisité par des artistes trans et non binaires.",
                "release_year": "2020",
                "origin_country": "Canada",
                "rating": 6.8,
            },
        ],
    },
    "lesbiennes": {
        "title": "Lesbiennes",
        "items": [
            {
                "tmdb_id": 31609,
                "title": "The Watermelon Woman",
                "poster_url": None,
                "overview": "Un documentaire autofictionnel lesbien noir pionnier.",
                "release_year": "1996",
                "origin_country": "États-Unis",
                "rating": 7.0,
            },
            {
                "tmdb_id": 440298,
                "title": "Portrait de la jeune fille en feu",
                "poster_url": None,
                "overview": "Une peintre et son modèle s'aiment loin du regard patriarcal.",
                "release_year": "2019",
                "origin_country": "France",
                "rating": 8.2,
            },
        ],
    },
    "queers": {
        "title": "Queers",
        "items": [
            {
                "tmdb_id": 76203,
                "title": "Paris is Burning",
                "poster_url": None,
                "overview": "La scène ballroom new-yorkaise entre voguing, luttes, et family.",
                "release_year": "1990",
                "origin_country": "États-Unis",
                "rating": 8.1,
            },
            {
                "tmdb_id": 70070,
                "title": "Gun Hill Road",
                "poster_url": None,
                "overview": "Une adolescente trans latine affronte sa famille et sa ville.",
                "release_year": "2011",
                "origin_country": "États-Unis",
                "rating": 6.7,
            },
        ],
    },
}
