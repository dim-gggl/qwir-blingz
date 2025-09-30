# Qwir Blingz

Community-driven universe celebrating LGBTQIA++ lives, centering sharing, planets, and radical inclusion.

## Current focus
- Scaffolding the Django project and foundational domain models (accounts, planets, media catalog).
- Building the TMDb integration layer (`backend/tmdb`) to power dynamic identity-based film discovery.

## Environment
1. Copy `.env.example` to `.env` (or export equivalent environment variables).
2. Supply a `TMDB_API_KEY` from [TMDb](https://www.themoviedb.org/documentation/api).
3. Adjust `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and database settings as needed.

## Development
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/base.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Next steps
- Wire the builder API into the Tailwind/Shadcn front-end experience.
- Connect `enqueue_planet_generation` to the real art pipeline and task queue.
- Expand automated coverage (celery task integration, multi-member planet flows).

## Tests
- `python manage.py test planets.tests.test_serializers planets.tests.test_views`

The builder API lives under `/api/planets/<id>/builder/...` once the server is running.