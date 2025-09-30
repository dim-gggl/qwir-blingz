<!-->
  ##############################################################################
  #             /$$$$$$$$ /$$      /$$ /$$$$$$$  /$$$$$$$ 
  #            |__  $$__/| $$$    /$$$| $$__  $$| $$__  $$
  #               | $$   | $$$$  /$$$$| $$  \ $$| $$  \ $$
  #               | $$   | $$ $$/$$ $$| $$  | $$| $$$$$$$ 
  #               | $$   | $$  $$$| $$| $$  | $$| $$__  $$
  #               | $$   | $$\  $ | $$| $$  | $$| $$  \ $$
  #               | $$   | $$ \/  | $$| $$$$$$$/| $$$$$$$/
  #               |__/   |__/     |__/|_______/ |_______/ 
  #                     /$$$$$$      /$$$$$$$  /$$$$$$           
  #                    /$$__  $$    | $$__  $$|_  $$_/           
  #                   | $$  \ $$    | $$  \ $$  | $$             
  #                   | $$$$$$$$    | $$$$$$$/  | $$             
  #                   | $$__  $$    | $$____/   | $$             
  #                   | $$  | $$    | $$        | $$             
  #                   | $$  | $$ /$$| $$ /$$   /$$$$$$ /$$       
  #                   |__/  |__/|__/|__/|__/  |______/|__/      
  #
  #           SOME EXPERIMENTS THAT HAVE BEEN MADE PRIOR TO START THIS PROJECT
  #                                   api.py
  ###############################################################################
</!-->

```python

import requests, random, json
from bs4 import BeautifulSoup
from models import Movie
from config import (
    HEADERS,
    MOVIE_URL, FLTR,
    BASE_URL_FOR_HOMEPAGE,
    KWORDS_BASE_URL as kwurl
    )


def query_content(url: str) -> dict | None:
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Erreur {response.status_code} - {response.reason}")

def list_of_movies_ids(url_no_page: str) -> list:
    count = 1
    movies_ids = []
    while count:
        try:
            movies_data = [
                elem["id"] for elem in query_content(
                    url_no_page + str(count)
                )["results"]
                ]
            if not movies_data or len(movies_data) < 1:
                count = 0
                return movies_ids
            else:
                movies_ids.extend(movie_data)
                count += 1
        except:
            raise TypeError(
                "Since the request has failed, there's no data to map. "
                "Check on the url you provided, or your headers, maybe."
                )
    return movies_ids

def init_homepage_list_of_movies_dict():
    queer_movies_ids = list_of_movies_ids(BASE_URL_FOR_HOMEPAGE)
    random_queer_movies = movies_details_from_ids(queer_movies_ids)
    return random_queer_movies

def movies_details_from_ids(ids: list[str]) -> list[dict]:
    """
    Effectue les requêtes pour obtenir des dict avec les ressources
    pour une liste d'ids passés en arguments.
    :param: list: liste d'ids de films.
    :retourne: list: liste de dict json avec les détails des films
    """
    movies = []
    for i in range(len(ids)):
        url = f"{MOVIE_URL}/{ids[i]}?{FLTR["fr"]}"
        movie = query_content(url)
        movies.append(movie)
    return movies

def movies_from_ids(ids: list[str]) -> list[Movie]:
    movies = []
    new_ids = []
    count = 0
    for id in ids:
        try:
            movie = Movie.query.get(id)
            if movie:
                movies.append(movie)
            else:
                new_ids.append(id)
        except Exception as e:
            print(e)
    if new_ids:
        for movie_dict in movies_details_from_ids(new_ids):
            movie = Movie(**movie_dict)
            movies.append(movie)
            Movie.query.session.add(movie)
            count += 1
            print(
                f"\n\n{'NOUVEAU FILM':^80}"
                f"\n{movie.title:^80}\n"
            )
    return movies

def db_movies_obj_from(ids:list[str]) -> list[Movie]:
    return [Movie.query.get(id) for id in ids]


def movies_selection(url):
    movies_ids = list_of_movies_ids(url)
    random_movies = movies_details_from_ids(movies_ids)
    return random_movies

def random_movie_from_list(movies_dict:list[dict | None]) -> Movie:
    random.shuffle(movies_dict)
    data = [dict_ for dict_ in movies_dict if type(dict_) == dict][0]
    homepage_random_movie = Movie(**data)
    return homepage_random_movie
```
<!-->
  ###########################################################################################
  #
  #              /$$      /$$                 /$$           /$$
  #             | $$$    /$$$                | $$          | $$
  #             | $$$$  /$$$$  /$$$$$$   /$$$$$$$  /$$$$$$ | $$  /$$$$$$$
  #             | $$ $$/$$ $$ /$$__  $$ /$$__  $$ /$$__  $$| $$ /$$_____/
  #             | $$  $$$| $$| $$  \ $$| $$  | $$| $$$$$$$$| $$|  $$$$$$
  #             | $$\  $ | $$| $$  | $$| $$  | $$| $$_____/| $$ \____  $$
  #             | $$ \/  | $$|  $$$$$$/|  $$$$$$$|  $$$$$$$| $$ /$$$$$$$/
  #             |__/     |__/ \______/  \_______/ \_______/|__/|_______/
  #
  #                 THE MODELS ON WHICH THESE EXPERIMENTS WERE BASED ON
  ###########################################################################################
</!-->

```python
import inspect, random, os, colorsys
from collections import Counter
from setter_helper import set_poster_path, load_credits
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from utils import COUNTRIES, enumerate_names, timed
from functools import cached_property



db = SQLAlchemy()

class Movie(db.Model):
    __tablename__ = 'Movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    original_title = db.Column(db.String, nullable=True)
    origin_country = db.Column(JSON, nullable=True)
    release_date = db.Column(db.String, nullable=True)
    runtime = db.Column(db.Integer, nullable=True)
    spoken_languages = db.Column(JSON, nullable=True)
    poster_path = db.Column(db.String, nullable=True)
    genres = db.Column(JSON, nullable=True)
    imdb_id = db.Column(db.String, nullable=True)
    homepage = db.Column(db.String, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    adult = db.Column(db.Boolean, default=False)
    video = db.Column(db.Boolean, default=False)
    budget = db.Column(db.Integer, nullable=True)
    vote_average = db.Column(db.Float, default=0.0)
    vote_count = db.Column(db.Integer, default=0)
    popularity = db.Column(db.Float, nullable=True)
    tagline = db.Column(db.String, nullable=True)
    revenue = db.Column(db.Integer, nullable=True)
    private = db.Column(JSON, nullable=True)

    def __init__(self, **data):
        self.private = {}
        for key, value in data.items():
            setattr(self, key, value)
        if not self.original_title:
            self.original_title = self.title
        self.private["_images_request_url"] = f"https://api.themoviedb.org/3/movie/{self.id}/images"
        self.private["_poster_url"] = set_poster_path(self.private.get("_images_request_url"))
        cast, crew, directors = load_credits(self.id, self.title) or (
            "Données manquantes", "Informations absentes", "Détails manquants"
        )
        self.private["_credits"] = (cast, crew, directors)

    @property
    def images_request_url(self):
        return self.private["_images_request_url"]

    @property
    def poster_url(self):
        return self.private['_poster_url']

    @property
    def cast(self):
        return [elem[0] for elem in self.private["_credits"][0]]

    @cast.setter
    def cast(self, value: tuple) -> list[tuple]:
        self.private["_credits"] = value
        return self.private["_credits"][0]

    @property
    def crew(self):
        return self._crew

    @crew.setter
    def crew(self, value):
        self.crew = value

    @property
    def directors(self):
        return self._directors

    @directors.setter
    def directors(self, value):
        self._directors = value

    @property
    def credits(self):
        return self.cast, self.crew, self.directors

    @property
    def release_year(self):
        return int(self.release_date.split("-")[0])

    @property
    def tmdb_link(self):
        return f"https://www.themoviedb.org/movie/{self.id}"

    @property
    def genre(self):
        genres = [elem["name"] for elem in self.genres]
        return enumerate_names(genres)

    @property
    def is_short(self):
        return self.runtime <= 30

    @property
    def is_medium(self):
        return 60 >= self.runtime >= 31

    @property
    def is_long(self):
        return self.runtime > 60

    def directed_by(self):
        return enumerate_names(self.directors)

    def actors(self, full=False):
        if isinstance(self.cast, list):
            if not full:
                return enumerate_names(self.cast[:5])
            else:
                return [tupl[0] for tupl in self.cast]
        else:
            print(self.cast)
            return enumerate_names(list(self.cast[:5]))

    def countries(self):
        if len(self.origin_country) > 1:
            origin_countries = [country for country in self.origin_country]
            return enumerate_names(origin_countries)
        elif len(self.origin_country) == 1:
            return COUNTRIES.get(self.origin_country[0])
        else:
            return None

    def imdb_link(self):
        if self.imdb_id:
            return f"https://www.imdb.com/fr/title/{self.imdb_id}"
        else:
            return None

    def to_dict(self) -> dict:
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data.update(self.private)
        for name, prop in inspect.getmembers(self.__class__, lambda o: isinstance(o, property)):
            data[name] = getattr(self, name)
        return data

    def __repr__(self):
        return f"<Movie: {self.title} ({self.release_date}) - ID: {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, Movie):
            return NotImplemented
        return self.id == other.id and self.title == other.title

    def __hash__(self):
        if self.id:
            token = ".".join([self.title, str(self.id)])
        elif not self.id and self.release_date:
            token = ".".join([self.title, str(self.release_date)])
        else:
            token = ".".join([_ for _ in self.title])
        return hash(token)


class MovieList(db.Model):
    themes = db.Column(JSON, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    movies_ids = db.Column(JSON, nullable=False)
    id = db.Column(db.String, primary_key=True)

    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)
        self.movies_ids = data.get("movies_ids", [])
        self.css_names = self.css_name()
        self.id = "&".join([theme[:2] for theme in self.themes])
        self._movies = [
            Movie.query.get(movie_id) for movie_id in self.movies_ids
            ]

    @cached_property
    def movies(self):
        return Movie.query.filter(Movie.id.in_(self.movies_ids)).all()

    @property
    def hashtags(self):
        return [f"#{theme.lower()} " for theme in self.themes]

    @timed("Sélection de films")
    def selection(self):
        movies = self.movies
        if len(movies) <= 12:
            return movies
        return random.sample(movies, 12)

    def css_name(self):
        css_name = self.name.lower().split(" ")[:5]
        return "-".join([name for name in css_name])

    def __add__(self, obj_movie: list[Movie] | Movie ):
        if isinstance(obj_movie, list) and len(obj_movie) >= 1:
            to_add = []
            for movie in obj_movie:
                if not isinstance(movie, Movie):
                    print("Une liste de films ne peut contenir que des films")
                elif movie.id not in self.movies_ids:
                    to_add.append(movie.id)
                else:
                    print("Une liste de films ne peut contenir de doublons")
            self.movies_ids.extend(to_add)
        elif isinstance(obj_movie, Movie):
            if obj_movie.id not in self.movies_ids:
                self.movies_ids.append(obj_movie.id)
            else:
                print("Une liste de films ne peut contenir de doublons")
        else:
            raise TypeError(f"{self.name} ne peut ajouter que des films")

        self._movies = [Movie.query.get(movie_id) for movie_id in self.movies_ids]
        return self

    def __repr__(self):
        return f"<MovieList Object ({len(self.movies)} movies) - {self.id}>"

    def __str__(self):
        return f"{self.name} - Sélection de {len(self.movies)} films"

    def __iter__(self):
        return iter(self.movies)



class MovieWorker:
    def __init__(self, name, imdb_url, profile_url):
        self.name = name
        self.imdb_url = imdb_url
        self.profile_url = profile_url



class Actor(MovieWorker):
    pass



class Staff(MovieWorker):
    def __init__(self, name, imdb_url, profile_url, job):
        super().__init__(name, imdb_url, profile_url)
        self.job = job



class Planet:
    def __init__(self, commu: MovieList):
        self.movie_list = commu
        self.name = self.movie_list.id
        self.id = self.movie_list.id
        self.icon = f"static/icons/{self.id}.png"
        self.image = f"static/planets/{self.id}.png"



class Community:
    COMMUNITIES = (
        "lesb",
        "trans",
        "bisex",
        "gay",
        "intersex",
        "asex",
        "non-bin",
        "gender-flu",
        "tds",
        "feminist",
        "queer",
        "pansex"
    )

    def __init__(self, name: str):
        self.name = ""
        i = 0
        while not self.name:
            if i < len(Community.COMMUNITIES):
                comu = Community.COMMUNITIES[i]
                if name == comu or comu in name:
                    self.name = comu
                else:
                    i += 1
            else:
                print(
                    f"{'Nom invalide':^80}\n{name:^80}\n"
                    f"{'Choix possible':^80}"
                )
                for com in Community.COMMUNITIES:
                    print(f"{com:^80}\n")
        movie_lists = MovieList.query.all()
        for liste in movie_lists:
            for theme in liste.themes:
                if self.name in liste.name or self.name in theme:
                    self.movie_list = liste
        self.id = [key for key, value in commu_by_id.items() if value == self.name].pop()
        self.planet = Planet(self)

    def __eq__(self, other):
        if not isinstance(other, Community):
            return NotImplemented
        return self.name == other.name and self.planet == other.planet

    def __hash__(self):
        token = self.name + self.movie_list.name
        return hash(token)
```
<!-->
  ###########################################################################################
  #
  #              /$$$$$$   /$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$  /$$$$$$ 
  #             /$$__  $$ /$$__  $$| $$$ | $$| $$_____/|_  $$_/ /$$__  $$
  #            | $$  \__/| $$  \ $$| $$$$| $$| $$        | $$  | $$  \__/
  #            | $$      | $$  | $$| $$ $$ $$| $$$$$     | $$  | $$ /$$$$
  #            | $$      | $$  | $$| $$  $$$$| $$__/     | $$  | $$|_  $$
  #            | $$    $$| $$  | $$| $$\  $$$| $$        | $$  | $$  \ $$
  #            |  $$$$$$/|  $$$$$$/| $$ \  $$| $$       /$$$$$$|  $$$$$$/
  #             \______/  \______/ |__/  \__/|__/      |______/ \______/ 
  #
  #                               config.py
  ###########################################################################################
</!-->
```python

import os
import json


os.environ["TMDB_BEARER"] = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjMTU1NDUwYzljZmE1ZjU0OGVmMTA3NTVjYzZkNmM5MyIsIm5iZiI6MTc0Mjg1ODU5Ny4zNzYsInN1YiI6IjY3ZTFlOTY1NGM1Mjc0NjY2NWRjNjkxYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.7MxDXARYWrIHhsIfiDC2j5y5k9ECcq2PTlCC9QXNXzU"


"""HEADERS for the API request"""
HEADERS = {
    "accept": 'application/json',
    "Authorization": 'Bearer ' + os.environ["TMDB_BEARER"]
}

"""URL Components to build a request to the API"""
# Domain
DOMAIN = "https://api.themoviedb.org"


# Endpoints
ENDPTS = {
    "v3": "/3",
    "v4": "/4",
    "discover": "/discover",
    "movie": "/movie",
    "tv": "/tv",
    "people": "/people"
}
MOVIE_URL = DOMAIN + ENDPTS["v3"] + ENDPTS["movie"]
DISCOVER_URL = f"{DOMAIN}{ENDPTS['v3']}{ENDPTS['discover']}{ENDPTS["movie"]}"
GENRES_URL = f"{DOMAIN}/3/genre/movie/list?language=fr"
SEARCH_URL = f"https://www.themoviedb.org/search{ENDPTS["movie"]}?language=fr-FR&query="

EXTERNAL_IDS_URL = "https://api.themoviedb.org/3/movie/830/external_ids"
KEYWORDS = "https://api.themoviedb.org/3/movie/830/keywords"
SIMILAR = "https://api.themoviedb.org/3/movie/830/similar?language=fr-FR&page=2321"
STREAMING = "https://api.themoviedb.org/3/movie/830/watch/providers"
MULTI_SEARCH_BY_KEYWORD = f"https://api.themoviedb.org/3/search/multi?query={'queer'}&include_adult=false&language=fr-FR&page=1"

# Filters by values
FLTR = {
        "adult_on": "include_adult=true",
        "adult_off": "include_adult=false",
        "video_on": "include_video=true",
        "video_off": "include_video=false",
        "certif": "certification=",
        "certif_country": "certification_country=",
        "fr": "language=fr-FR",
        "en": "language=en-US",
        "prim_release": "primary_release_year=",
        "page": "page=",
        "by_pop": "sort_by=popularity.desc",
        "by_pop_rev": "sort_by=popularity.asc",
        "by_vote": "sort_by=vote_average.desc",
        "by_vote_rev": "sort_by=vote_average.asc",
        "by_vote_count": "sort_by=vote_count.desc",
        "by_vote_count_rev": "sort_by=vote_count.asc",
        "by_title": "sort_by=title.desc",
        "by_title_rev": "sort_by=title.asc",
        "by_revenue": "sort_by=revenue.desc",
        "by_revenue_rev": "sort_by=revenue.asc",
        "after": "primary_release_date.gte=",
        "before": "primary_release_date.lte=",
        "num_vote_max": "vote_count.lte=",
        "num_vote_min": "vote_count.gte=",
        "from": "with_origin_country=",
        "genre": "with_genres=",
        "about": "with_keywords="
    }

TOPPIC = {
    "same-sex-relationship": 271167,    # DONE lgbt
    "same-sex-parenthood": 325395,      # DONE lgbt
    "same-sex-marriage": 253337,        # DONE lgbt
    "same-sex-attraction": 236454,      # DONE lgbt
    "gay-theme": 258533,                # DONE gay
    "girl-on-girl": 155265,             # DONE lesbians
    "sexual-repression": 18732,         # DONE discrimiations
    "gender-identity": 210039,          # gender
    "gender-studies": 246413,           # gender
    "hiv": 9766,                        # hiv
    "hiv-aids-epidemic": 262235,         # hiv

    "aids": 740,

    "asex aromantic": 329976,
    "asexual": 329977,
    "asexuality": 247099,
    "aromantic-asexual": 322171,

    "racism arab-lgbt": 316515,
    "racism anti-racism": 257456,
    "racism anti-semitism": 10144,
    "racism black": 272309,
    "racism black-activist": 11550,
    "racism black-lgbt": 195624,
    "racism black-lives-matter": 233840,
    "racism black-woman": 291081,

    "bisexual": 329968,
    "bisexual-man": 168812,
    "bisexual-woman": 287417,
    "bisexuality": 3183,

    "drag cross_dressing": 12090,
    "drag": 171636,
    "drag-queen": 824,

    "gender-discrimination": 299718,
    "sexual-discrimation": 225710,
    "class-discrimination": 215773,
    "institutional-discrimination": 10057,
    "discrimination homophobia": 1013,
    "feminism misogyny": 161166,
    "feminism patriarchy": 6337,
    "feminism patriarchal-society": 338884,
    "feminism incel": 244355,
    "discrimination homophobic-attack":252375,
    "gay closeted": 299604,
    "queer coming-out": 1862,
    "trans gay conversion-therapy": 238832,

    "feminism": 2383,
    "feminism feminist": 11718,
    "feminism feminist-movement": 301659,
    "global-feminism": 293179,
    "radical-feminism": 309966,
    "feminism queer intersectionality": 228965,
    "feminism patriarchy": 6337,
    "feminism abortion": 208591,
    "feminism abortion-clinic": 221195,
    "feminism abortion-history": 296536,

    "gay-artist": 259285,                   # Gay, CULTURE, ART
    "gay-liberation": 173672,               # Gay, COMMUNAUTY, HISTORY
    "gay-rights": 264411,                   # Gay, COMMUNAUTY, JUSTICE, HISTORY
    "gay-youth": 247821,                    # Gay, EDUCATION, TRAUMA
    "gay-history": 241179,                  # Gay, COMMUNAUTY, HISTORY
    "gay-subtext": 326218,                  # Gay, HIDDEN, SHAME
    "male-homosexuality": 10180,            # Gay, SEXUALITY, IDENTITY
    "homosexual-father": 293495,            # Gay, FATHERHOOD, FAMILY, EDUCATION
    "homoerotic": 267923,                   # Gay, SEXUALITY, EROTICISM, FETISH
    "homosexual": 272617,                   # Homosexual, GENERAL
    "closeted-homosexual": 239239,          # Gay, HIDDEN, SHAME
    "homosexuality": 275157,                # Homosexual, GENERAL
    "homoerotism": 250937,                  # Gay, SEXUALITY, EROTICISM, FETISH
    "homoeroticism": 157096,                # Gay, SEXUALITY, EROTICISM, FETISH

    "gender": 34214,
    "intersex gender-affirmation surgery": 273188,
    "gender-identity": 210039,
    "genderfluid": 281283,
    "genderqueer": 266529,
    "gender-roles": 34221,
    "gender-studies": 246413,
    "gender-transition": 234700,
    "non-binary": 252909,
    "genderfluid androgyny": 11402,
    "pan polyamory": 155870,
    "pansexual": 262765,

    "intersex": 240109,
    "intersex-child": 257264,
    "intersexuality": 9331,

    "lgbt": 158718,
    "lgbt-activism": 275749,
    "lgbt-history": 313433,
    "lgbt-rights": 280179,
    "lgbtq": 346871,
    "lgbtq+": 348563,
    "elderly-lgbt": 271115,
    "lgbt chosen-family": 267488,

    "lesb female-homosexuality": 15136,      # Lesbian, Lesbians, SEXUALITY, IDENTITY
    "lesbian": 264386,                  # Lesbian, Lesbians, GENERAL
    "lesbian-nun": 272066,              # Lesbian, Lesbians, RELIGION, PATRIARCHY
    "lesbian-relationship": 9833,       # Lesbian, Lesbians, HAPPINNESS
    "lesbian-affair": 290382,           # Lesbian, Lesbians, EMANCIPATION
    "lesbian-history": 305694,          # Lesbian, Lesbians, COMMUNAUTY, HISTORY
    "lesbian-prison": 283414,
    "lesbians": 308586,
    "lesbian_love": 315385,
    "lesbian_romance": 319872,
    "lesbian_subtext": 328765,
    "lesbian_culture": 345079,
    "lesb dykeumentary": 308587,

    "lgbt pride": 156501,

    "queer": 250606,                    # Queer, Queers, GENERAL
    "queer-cast": 312912,               # Queer, Queers, CULTURE, ART
    "queer-coded": 304694,              # Queer, Queers, COMMUNAUTY, CULTURE? IDENTITY
    "queer-and-questioning": 281814,    # Queer, Queers, SOCIETY, PSYCHOLOGY
    "queer-joy": 321567,                # Queer, Queers, HAPPINNESS
    "queer-revenge": 322221,            # Queer, Queers, JUSTICE, CATHARSIS
    "queer-friends": 333327,            # Queer, Queers, HAPPPINNESS
    "queer-romance": 333766,            # Queer, Queers, HAPPINNESS
    "queer-loneliness": 337238,         # Queer, Queers, SOCIETY, PSYCHOLOGY
    "queer-activism": 207958,           # Queer, Queers, JUSTICE COMMUNAUTY, HISTORY
    "queer-cinema": 300642,             # Queer, Queers, CULTURE, ART
    "queer-documentary": 346116,        # Queer, Queers, CULTURE, ART
    "queer-history": 314127,            # Queer, Queers, HISTORY, RIGHTS
    "queer-horror": 265587,             # Queer, Queers, CULTURE, ART
    "queer-love": 332049,               # Queer, Queers, HAPPINNESS
    "queer-sexuality": 347179,          # Queer, Queers, SEXUALITY, IDENTITY

    "tds prostitution": 13059,              # Sex-Work
    "tds sex-work": 271159,                 # Sex-Work
    "tds sex-worker": 13059,                # Sex-Work
    "tds sexworkers": 245541,
    "tds sex_work": 226543,
    "tds sex_worker": 190178,
    "tds escort-girl": 163791,
    "tds whore": 279793,
    "sex body-positivity": 254724,
    "sex cruising": 1886,

    "amor-trans": 349272,
    "trans dysphoria": 173531,
    "trans gender-dysphoria": 173531,             # Trans GENDER DYSPHORIA
    "trans gender-transition": 234700,            # Trans TRANSITION, SOCIETY, PSYCHOLOGY
    "trans": 265451,                        # Trans, GENERAL
    "trans-activism": 254152,               # Trans, COMMUNAUTY, JUSTICE
    "trans-documentary": 325300,            # Trans, CULTURE, ART
    "trans-femme": 317540,                  # Trans, Woman, GENDER, IDENTITY
    "trans-history": 328899,                # Trans, COMMUNAUTY, HISTORY
    "trans-lesbian": 307399,                # Trans, Lesbian, SEXUALITY, IDENTITY
    "trans-love": 343076,                   # Trans HAPPINNESS
    "trans-man": 217271,                    # Trans, Man, IDENTITY, GENDER
    "trans-man": 194530,                    # Trans, Man, IDENTITY, GENDER
    "trans-masculine": 316562,              # Trans, Man, IDENTITY, GENDER
    "trans-rights": 268076,                 # Trans, COMMUNAUTY, HISTORY
    "trans rights": 335948,                 # Trans, COMMUNAUTY, HISTORY
    "trans-woman": 189962,                  # Trans, Woman, GENDER, IDENTITY
    "trans-woman": 208798,                  # Trans, Woman, GENDER, IDENTITY
    "trans-women": 312909,                  # Trans, Woman, GENDER, IDENTITY
    "trans transfeminism": 271103,                # Trans, TRANSFEMINISM, FEMINISM
    "trans transidentity": 274776,                # Trans, IDENTITY
    "trans transgender": 14702,                   # Trans, GENDER, IDENTITY
    "trans transgender": 290527,                  # Trans, GENDER, IDENTITY
    "trans transgender-men": 321062,              # Trans, Man, IDENTITY, GENDER
    "trans transgender-rights": 229325,           # Trans, COMMUNAUTY, HISTORY
    "trans transitioning": 249055,                # Trans, TRANSITION, SOCIETY, PSYCHOLOGY
    "trans transmasc": 327419,                    # Trans, Masculine, GENDER, IDENTITY
    "trans transphobia": 10716,                   # Trans, DISCRIMINATION
    "trans-phobia": 208799,                 # Trans, DISCRIMINATION
    "trans-youth": 232375,                  # Trans, EDUCATION
    "trans-non-binary": 312910,             # Trans,Non-Binary, GENDER, IDENTITY
}


TPG_NRV = [
    'queer-activism', 'queer-history',
    'queer-and-questioning', 'lgbt-activism',
    'lgbt-rights', 'lgbt-history', 'gay-liberation',
    'gay-rights', 'trans-activism', 'trans-rights',
    'transgender-rights', 'transgender',
    'gender-studies', 'radical-feminism'
]

def toppics(args: list[str]) -> str:
    return "|".join([str(TOPPIC[arg]) for arg in args])
KWORDS_BASE_URL = f"{DISCOVER_URL}?{FLTR['fr']}&{FLTR['about']}"

def base_url(args: str | list[str]):
    return f"{KWORDS_BASE_URL}{keywords(word=args)}&{FLTR['by_pop']}&page="

def keywords(word=str | list[str] | tuple[str]) -> list:
    toppics = []
    if isinstance(word, str):
        for k, v in TOPPIC.items():
            if word in k:
                toppics.append(str(v))
    elif isinstance(word, (list, tuple)):
        for element in word:
            for k, v in TOPPIC.items():
                if element in k:
                    toppics.append(str(v))
    return "|".join(toppics)

BASE_URL_FOR_HOMEPAGE = base_url(["queer", "lgbt"])


# Filters by range
CERTIF_GTE_FILTER = "certification.gte="
CERTIF_LTE_FILTER = "certification.lte="
PRIM_REL_GTE_FILTER = "primary_release_date.gte="
PRIM_REL_LTE_FILTER = "primary_release_date.lte="

sort_by = {
    "pop-=": "popularity.asc",
    "pop+": "popularity.desc",
    "date-": "release_date.asc",
    "date+": "release_date.desc",
    "revenue-": "revenue.asc",
    "revenur+": "revenue.desc",
    "first_date-": "primary_release_date.asc",
    "first_date+": "primary_release_date.desc",
    "or_title-": "original_title.asc",
    "or_title+": "original_title.desc",
    "vote-": "vote_average.asc",
    "vote+": "vote_average.desc",
    "num_vote-": "vote_count.asc",
    "num_vote+": "vote_count.desc"
}

```