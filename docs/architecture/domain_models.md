# Domain Model Draft

## Accounts
- `accounts.User`: extends Django `AbstractUser` with privacy toggles for email, full name, gender identity, birth date, plus pronouns, bio, avatar, and timestamps.
- `accounts.TriggerTopic`: curated trigger topics (e.g., "sexual violence", "medical trauma") that can be maintained by moderators.
- `accounts.UserTriggerPreference`: user-specific avoidance preferences referencing curated topics or custom free-text labels.

## Planets
- `planets.Planet`: member-crafted worlds with slug, tagline, description, accent colors, media, visibility scope, and creator.
- `planets.PlanetAppearance`: structured visual/identity profile captured by the chatbot (colors, textures, rings, origin, emotional tone, assets).
- `planets.PlanetBuilderSession`: persistent builder state (step index, collected attributes, skips, confirmations).
- `planets.PlanetMembership`: through table capturing membership, stewardship roles, and invitation context.

## Media Catalog
- `media_catalog.IdentityTag`: global identity/thematic tags optionally mapped to TMDb keyword IDs for generator alignment.
- `media_catalog.MediaItem`: TMDb-backed film/series metadata snapshot with optional identity tag associations.
- `media_catalog.MediaList`: curated or dynamic (keyword-driven) collections with visibility controls and optional cover art.
- `media_catalog.MediaListItem`: ordering and annotations for items inside a list.

## Integration Hooks
- TMDb service layer (`backend/tmdb`) feeds `MediaItem` and `MediaList` generation pipelines.
- Trigger topics link to onboarding flows for safety configuration.
- Planets and media lists will surface on member profile pages with privacy-respecting toggles.
