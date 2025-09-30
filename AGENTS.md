# Repository Guidelines

## Project Principles
Qwir Blingz is a sharing-first universe built with and for LGBTQIA++, sex worker, disabled, and BIPOC communities. Every delivery must advance consent, mutual care, and self-expression. Anchor features in the planet metaphor: members craft planets, share stories, and surface minority-led media. Honor the TMDb-driven discovery pillar—authentication flows always tease a refreshable queer film so folks glimpse the galaxy awaiting them.

## Project Structure & Module Organization
Core Django code sits in `backend/`, with apps for `accounts`, `planets`, `media_catalog`, `tmdb`, and settings under `backend/config`. REST interfaces live in `backend/planets/api/`. TMDb helpers reside in `backend/tmdb`. Templates, Tailwind/Shadcn assets, and shared static files live in root `templates/` and `static/`, with the front-end scaffold evolving in `backend/frontend`. Architectural notes and domain briefs are under `docs/architecture/`—keep them current when behaviors shift.

## Build, Test, and Development Commands
- `cd backend && uv venv` creates the project virtualenv.
- `source .venv/bin/activate && uv pip sync requirements/base.txt` installs locked dependencies.
- `uv run manage.py migrate` applies schema updates.
- `uv run manage.py runserver` boots local development.
- `uv run manage.py test planets.tests.test_serializers planets.tests.test_views` runs the active suite; add modules as coverage grows.

## Coding Style & Naming Conventions
Stick to 4-space indentation, type hints where reasonable, and Django naming norms (models in PascalCase, helpers snake_case, URL names hyphenated like `planet-builder-start`). Keep services and serializers slim; push reusable prompts/config into dedicated modules (`backend/planets/services/builder.py`). When styling front-end templates, use strictly Tailwind utility classes and more specifically Shadcn component patterns for consistency and accessibility.

## Testing Guidelines
Place tests inside `backend/<app>/tests/` using `pytest` and using `fixtures` and a temp database to make sure he tests are always independent.. Name files `test_<area>.py`, methods `test_<behavior>`. Mock TMDb calls and async hooks (`enqueue_planet_generation`) to keep runs deterministic. Cover accessibility rules, trigger-topic validation, and builder state transitions whenever you touch related code.

## Commit & Pull Request Guidelines
Adopt Conventional Commit prefixes (`feat:`, `fix:`, `docs:`) with imperative subjects. Reference architecture docs, issues, or product notes in the body; call out safety or inclusion impacts explicitly. PRs should summarize scope, list endpoints or migrations, attach UI screenshots or recordings, confirm `uv pip sync` parity, and state which tests ran.

## TMDb & Planet Builder Focus
Guard the TMDb keyword discovery flow: require `TMDB_API_KEY`, throttle politely, and cache fallbacks so the welcome teaser never goes dark. Planet builder experiences must stay playful, trauma-aware, and accessible—persist `PlanetBuilderSession` data, respect skip/edit flows, and ensure generated prompts mirror the blueprint in `docs/architecture/planet_builder_chatbot.md` before triggering art tasks.
