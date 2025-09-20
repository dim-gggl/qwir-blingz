# Planet Builder State & API Plan

## Persistence Options
1. **Database-backed** (recommended for audit + multi-device support)
   - Model: `PlanetBuilderSession`
   - Fields: `planet`, `user`, `step_index`, `attributes` (JSON), `skipped_steps` (JSON), `confirmations` (JSON), `is_active`, `created_at`, `updated_at`.
   - Pros: durable, easy to query, fits relational migrations, no extra infrastructure.
   - Cons: slightly heavier writes for each message.
2. **Cache-backed** (Redis)
   - Store serialized `PlanetBuilderState` keyed by session.
   - Pros: lighter writes, natural expiration.
   - Cons: requires cache service, less audit trail.

Decision: start with DB-backed model; add caching later for performance.

## API Endpoints (REST)
- `POST /api/planets/<planet_id>/builder/start` — Initialize or resume a session.
- `POST /api/planets/<planet_id>/builder/step` — Submit response for current step; returns updated state + next prompt.
- `POST /api/planets/<planet_id>/builder/skip` — Mark step skipped, advance.
- `POST /api/planets/<planet_id>/builder/back` — Move to previous step.
- `POST /api/planets/<planet_id>/builder/goto` — Jump to named step (for editing).
- `POST /api/planets/<planet_id>/builder/confirm` — Finalize summary, trigger generation.
- `GET /api/planets/<planet_id>/builder/state` — Fetch current session snapshot.

Authentication: only the planet owner (and optionally stewards) can mutate. Use DRF permissions with `IsAuthenticated` + custom check.

## Serialization
- Serializer validates input per step (`color` regex, choice enforcement, etc.).
- On `step` submission, merge sanitized data into session `attributes`, then update related `PlanetAppearance` fields (draft mode).

## Generation Trigger
- When `confirm`, set `PlanetAppearance.status = generating`, store prompts, enqueue Celery task stub (`enqueue_planet_generation`).
- Return accepted summary + status `generating` to front-end.

## TODOs
- Integrate with real task queue and art generator once available.
- Add rate limiting / throttling for builder endpoints.
- Expand coverage for multi-user collaboration flows.

## Testing Strategy
- Serializer unit tests covering per-step validation, including color formats, tone choices, and trigger tag ID resolution.
- Viewset tests simulating the step/skip/back/confirm lifecycle with authenticated owners and unauthorized users.
- Integration test stub ensuring `enqueue_planet_generation` is invoked on confirm (mock the task function).
