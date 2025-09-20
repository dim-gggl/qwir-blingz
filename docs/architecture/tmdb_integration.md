# TMDb Integration Overview

## Goals
- Provide a reusable service layer that interacts with The Movie Database (TMDb) API.
- Support keyword-driven discovery (e.g., `Queer`, `Trans`, `Pansexuality`) with random movie sampling.
- Expose friendly helper methods for UI widgets (sign-in teaser panel, home carousels, planet landing pages).
- Remain framework-agnostic enough to plug into Celery tasks, Django views, or REST endpoints.

## Key Components
- `tmdb.clients.TmdbClient`: thin HTTP client wrapper using `httpx` with automatic API key injection.
- `tmdb.services.discovery`: higher-level functions for keyword lookup, cached keyword ID resolution, and random movie selection.
- `tmdb.models`: Django models to persist curated lists, cached keyword metadata, and sync audits (to be added when the Django project scaffold is ready).
- Background job hooks (Celery/async tasks) for scheduled syncs of curated collections and keyword caches.

## Data Flow
1. UI requests a themed list (e.g., "Queer" carousel).
2. Service resolves the keyword slug to a TMDb keyword ID (cached locally for performance).
3. Service calls `/discover/movie` with appropriate filters (language, adult content flags, release date ranges).
4. Response is normalized and returned to the caller. Optional persistence into our cache tables.
5. For "random" selections, the service fetches metadata for total pages, picks a random page/result, and returns detailed movie data.

## Configuration
- API key stored in `TMDB_API_KEY` environment variable; `.env.example` will document required keys.
- Optional config flags: default language (`TMDB_LANGUAGE`), request timeout, logging level.

## Error Handling & Resilience
- Wrap HTTP errors in custom exceptions (`TmdbError`, `TmdbAuthorizationError`, etc.) for easier handling in views/tasks.
- Rate-limit awareness: respect TMDb guidelines; add simple backoff on `429` responses.
- Safe defaults when the API is unavailable (fallback to cached or curated content).

## Security & Privacy
- API key never checked into repo; loaded via Django settings.
- Request/response logging sanitized to exclude API key and sensitive query params.

## Next Steps
- Scaffold `backend/` Django project and add `tmdb` app package.
- Implement `TmdbClient` with typed responses and error handling.
- Create service functions for keyword search and random movie selection.
- Add unit tests with mocked TMDb responses once testing framework is in place.
