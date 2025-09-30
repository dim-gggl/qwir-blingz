# TMDb Integration Overview

## Goals
- Provide a reusable service layer that interacts with The Movie Database (TMDb) API.
- Support keyword-driven discovery (e.g., `Queer`, `Trans`, `Pansexuality`) with random movie sampling.
- Expose friendly helper methods for UI widgets (sign-in teaser panel, feed carousels, planet landing pages).
- Remain framework-agnostic enough to plug into Celery tasks, Django views, or REST endpoints.

## Key Components
- `tmdb.clients.TmdbClient`: thin HTTP client wrapper using `httpx` with automatic API key injection.
- `tmdb.services.discovery`: higher-level functions for keyword lookup, cached keyword ID resolution, and random movie selection.
- `media_catalog.services.generate_media_list_for_identity`: orchestrates keyword resolution, movie detail normalization, and persistence into `MediaItem`, `MediaList`, and `MediaListItem` records for sharing-ready queer collections.
- `tmdb.models`: Django models to persist curated lists, cached keyword metadata, and sync audits (to be added when the Django project scaffold is ready).
- Background job hooks (Celery/async tasks) for scheduled syncs of curated collections and keyword caches.

## Media Catalog Synchronization
`generate_media_list_for_identity` is the first production pathway that turns TMDb discovery results into shareable lists inside Qwir Blingz. Given an `IdentityTag`, the service will:

1. Resolve and persist the associated TMDb keyword ID when missing.
2. Page through `/discover/movie` results until the requested limit is met, respecting adult-content toggles and language hints.
3. Hydrate full movie payloads (including credits, external IDs, watch providers) and normalize image URLs for consistent display.
4. Upsert matching `MediaItem` rows, tag them with the originating identity, and synchronize a dynamic `MediaList` (slugged `<tag>-spotlight-<id>`) with stable ordering for front-end carousels.

The service runs inside a transaction so the list, items, and many-to-many joins update atomically. Callers can inject a preconfigured `TmdbClient` (e.g., within a Celery task) or rely on the default helper that reads configuration from Django settings.

## Data Flow
1. UI requests a themed list (e.g., "Queer" carousel on the member feed).
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
- Expose the list generation service via REST and Celery entry points so curators can trigger syncs on demand.
- Add caching for keyword lookups and movie detail responses to reduce API chatter.
- Extend discovery to TMDb TV endpoints and integrate maturity filters informed by safety preferences.
- Affiner les pages thématiques (regroupements par format/genre, accessibilité, pagination) et préparer les déclinaisons séries.
