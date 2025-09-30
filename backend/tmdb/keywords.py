"""
TMDb Keywords mapping based on previous experiments.
Contains comprehensive keyword IDs for LGBT+ themes.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# Complete keyword mapping from previous experiments
TMDB_KEYWORDS = {
    # Same-sex relationships
    "same-sex-relationship": 271167,
    "same-sex-parenthood": 325395,
    "same-sex-marriage": 253337,
    "same-sex-attraction": 236454,

    # Gay themes
    "gay-theme": 258533,
    "gay-artist": 259285,
    "gay-liberation": 173672,
    "gay-rights": 264411,
    "gay-youth": 247821,
    "gay-history": 241179,
    "gay-subtext": 326218,
    "male-homosexuality": 10180,
    "homosexual-father": 293495,
    "homoerotic": 267923,
    "homosexual": 272617,
    "closeted-homosexual": 239239,
    "homosexuality": 275157,
    "homoerotism": 250937,
    "homoeroticism": 157096,

    # Lesbian themes
    "girl-on-girl": 155265,
    "female-homosexuality": 15136,
    "lesbian": 264386,
    "lesbian-nun": 272066,
    "lesbian-relationship": 9833,
    "lesbian-affair": 290382,
    "lesbian-history": 305694,
    "lesbian-prison": 283414,
    "lesbians": 308586,
    "lesbian_love": 315385,
    "lesbian_romance": 319872,
    "lesbian_subtext": 328765,
    "lesbian_culture": 345079,
    "dykeumentary": 308587,

    # Asexual themes
    "asex-aromantic": 329976,
    "asexual": 329977,
    "asexuality": 247099,
    "aromantic-asexual": 322171,

    # Bisexual themes
    "bisexual": 329968,
    "bisexual-man": 168812,
    "bisexual-woman": 287417,
    "bisexuality": 3183,

    # Pansexual themes
    "pansexual": 262765,
    "polyamory": 155870,

    # Trans themes
    "amor-trans": 349272,
    "trans-dysphoria": 173531,
    "gender-dysphoria": 173531,
    "gender-transition": 234700,
    "trans": 265451,
    "trans-activism": 254152,
    "trans-documentary": 325300,
    "trans-femme": 317540,
    "trans-history": 328899,
    "trans-lesbian": 307399,
    "trans-love": 343076,
    "trans-man": 217271,
    "trans-masculine": 316562,
    "trans-rights": 268076,
    "trans-woman": 189962,
    "trans-women": 312909,
    "transfeminism": 271103,
    "transidentity": 274776,
    "transgender": 14702,
    "transgender-men": 321062,
    "transgender-rights": 229325,
    "transitioning": 249055,
    "transmasc": 327419,
    "transphobia": 10716,
    "trans-phobia": 208799,
    "trans-youth": 232375,
    "trans-non-binary": 312910,

    # Gender themes
    "gender": 34214,
    "intersex-gender-affirmation-surgery": 273188,
    "gender-identity": 210039,
    "genderfluid": 281283,
    "genderqueer": 266529,
    "gender-roles": 34221,
    "gender-studies": 246413,
    "non-binary": 252909,
    "androgyny": 11402,

    # Intersex themes
    "intersex": 240109,
    "intersex-child": 257264,
    "intersexuality": 9331,

    # LGBT general
    "lgbt": 158718,
    "lgbt-activism": 275749,
    "lgbt-history": 313433,
    "lgbt-rights": 280179,
    "lgbtq": 346871,
    "lgbtq+": 348563,
    "elderly-lgbt": 271115,
    "lgbt-chosen-family": 267488,
    "lgbt-pride": 156501,

    # Queer themes
    "queer": 250606,
    "queer-cast": 312912,
    "queer-coded": 304694,
    "queer-and-questioning": 281814,
    "queer-joy": 321567,
    "queer-revenge": 322221,
    "queer-friends": 333327,
    "queer-romance": 333766,
    "queer-loneliness": 337238,
    "queer-activism": 207958,
    "queer-cinema": 300642,
    "queer-documentary": 346116,
    "queer-history": 314127,
    "queer-horror": 265587,
    "queer-love": 332049,
    "queer-sexuality": 347179,

    # Sex work themes
    "prostitution": 13059,
    "sex-work": 271159,
    "sex-worker": 13059,
    "sexworkers": 245541,
    "sex_work": 226543,
    "sex_worker": 190178,
    "escort-girl": 163791,
    "whore": 279793,

    # Drag themes
    "cross-dressing": 12090,
    "drag": 171636,
    "drag-queen": 824,

    # Feminism themes
    "feminism": 2383,
    "feminist": 11718,
    "feminist-movement": 301659,
    "global-feminism": 293179,
    "radical-feminism": 309966,
    "intersectionality": 228965,
    "patriarchy": 6337,
    "patriarchal-society": 338884,
    "abortion": 208591,
    "abortion-clinic": 221195,
    "abortion-history": 296536,

    # Discrimination themes
    "sexual-repression": 18732,
    "gender-discrimination": 299718,
    "sexual-discrimination": 225710,
    "class-discrimination": 215773,
    "institutional-discrimination": 10057,
    "homophobia": 1013,
    "misogyny": 161166,
    "incel": 244355,
    "homophobic-attack": 252375,
    "closeted": 299604,
    "coming-out": 1862,
    "conversion-therapy": 238832,

    # Race and ethnicity with LGBT
    "arab-lgbt": 316515,
    "anti-racism": 257456,
    "anti-semitism": 10144,
    "black": 272309,
    "black-activist": 11550,
    "black-lgbt": 195624,
    "black-lives-matter": 233840,
    "black-woman": 291081,

    # HIV/AIDS themes
    "hiv": 9766,
    "hiv-aids-epidemic": 262235,
    "aids": 740,

    # Sex and body positivity
    "body-positivity": 254724,
    "cruising": 1886,
}

# Thematic groupings from experiments
QUEER_ACTIVISM_KEYWORDS = [
    207958,  # queer-activism
    314127,  # queer-history
    281814,  # queer-and-questioning
    275749,  # lgbt-activism
    280179,  # lgbt-rights
    313433,  # lgbt-history
    173672,  # gay-liberation
    264411,  # gay-rights
    254152,  # trans-activism
    268076,  # trans-rights
    229325,  # transgender-rights
    14702,   # transgender
    246413,  # gender-studies
    309966,  # radical-feminism
]


def get_keywords_for_theme(theme_slug: str) -> List[int]:
    """
    Get TMDb keyword IDs for a given theme slug.
    Returns a list of related keyword IDs based on the theme.
    """
    keyword_map = {
        "trans-joy": [
            265451, 343076, 254152, 268076, 335948,
            274776, 14702, 290527, 325300, 317540,
            328899, 307399, 217271, 189962, 312909
        ],
        "lesbian-love": [
            264386, 308586, 315385, 319872, 9833,
            15136, 305694, 328765, 345079, 308587,
            290382, 272066
        ],
        "gay-celebration": [
            258533, 10180, 275157, 173672, 264411,
            241179, 259285, 326218, 293495, 267923,
            272617, 239239, 250937, 157096
        ],
        "queer-joy": [
            250606, 321567, 333327, 333766, 332049,
            312912, 300642, 346116, 304694, 207958,
            314127, 265587, 347179
        ],
        "lgbt-history": [
            158718, 346871, 348563, 275749, 313433,
            280179, 156501, 267488, 271115, 271167,
            325395, 253337, 236454
        ],
        "non-binary": [
            252909, 266529, 281283, 210039, 34221,
            312910, 34214, 234700, 11402
        ],
        "gender-studies": [
            246413, 34214, 210039, 234700, 34221,
            273188, 299718, 11402
        ],
        "radical-feminism": [
            309966, 2383, 11718, 301659, 293179,
            228965, 6337, 338884, 161166, 208591,
            221195, 296536
        ],
        "intersex": [
            240109, 257264, 9331, 273188
        ],
        "asexual": [
            329977, 247099, 329976, 322171
        ],
        "tds-sex-work": [
            271159, 13059, 245541, 226543, 190178,
            163791, 279793, 254724
        ],
        "bisexual": [
            329968, 168812, 287417, 3183
        ],
        "pansexual": [
            262765, 155870
        ],
        "disability-joy": [
            # Note: Limited disability representation in original experiments
            # Would need additional TMDb keyword research
        ],
        "bipoc-lgbtq": [
            316515, 195624, 272309, 291081, 233840,
            11550, 257456, 10144
        ],
    }

    return keyword_map.get(theme_slug, [])


def get_primary_keyword_for_theme(theme_slug: str) -> Optional[int]:
    """Get the primary TMDb keyword ID for a theme."""
    keywords = get_keywords_for_theme(theme_slug)
    return keywords[0] if keywords else None


def build_tmdb_keyword_filter(keyword_ids: List[int]) -> str:
    """Build TMDb API keyword filter string from keyword IDs."""
    if not keyword_ids:
        return ""
    return "|".join(str(kid) for kid in keyword_ids)