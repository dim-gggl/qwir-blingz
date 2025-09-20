# Planet Appearance Model Draft

## Goals
- Capture structured data from the chatbot-assisted planet builder so visuals and lore are reproducible.
- Support asset generation workflows (hero image + icon) and allow re-generation when identity evolves.
- Encode accessible metadata (tone, safety notes) that informs discovery and trigger filtering.

## Proposed Fields (Planets.PlanetAppearance)
- `planet` (OneToOneField to `Planet`, primary key) — each planet has a single current appearance record.
- `name` (CharField) — planet display name (can diverge from `Planet.name` if needed for localization).
- `tagline` (CharField) — short poetic statement used in carousels.
- `motto` (CharField) — optional slogan or mantra.
- `primary_color` / `secondary_color` (CharField) — HEX values (#RRGGBB) selected by the chatbot.
- `palette` (JSONField) — array of additional swatches `{name, hex, rgb}` for gradients or accents.
- `surface_type` (CharField with choices: gas, ice, oceanic, rocky, metallic, organic, crystalline, hybrid).
- `surface_descriptors` (Array/JSON) — ordered list of adjectives provided by the user (e.g., glossy, mossy, embroidered).
- `ring_style` (CharField with choices: none, single, double, multiple, fragmented, halo) plus `ring_descriptors` (JSON) and `ring_color` (CharField).
- `has_moons` (BooleanField) / `moon_count` (PositiveSmallIntegerField, nullable) / `moon_descriptors` (JSON) — expressive details about satellites.
- `atmosphere_style` (CharField choices: aurora, nebula, stormy, calm, glowing, vaporwave, none) with `atmosphere_descriptors` (JSON).
- `origin_type` (CharField choices: natural, crafted, reclaimed, bioengineered, ritual, unknown).
- `materials` (JSON) — list of material descriptors (e.g., "hand-carved cedar", "reclaimed copper").
- `emotional_tone` (CharField choices: sanctuary, rebellious, jubilant, reflective, fiery, tender, enigmatic, custom) with optional `emotional_custom_label` (CharField).
- `accessibility_notes` (TextField) — inclusive description for screen readers and to provide sensory orientation.
- `trigger_avoidance_tags` (ManyToMany to `accounts.TriggerTopic`, blank=True) — hide this planet from folks who opt out of specific content.
- `custom_trigger_warnings` (JSON) — free-form warnings tied to user preferences.
- `hero_image` (ImageField, nullable) — generated full render.
- `icon_image` (ImageField, nullable) — badge/sigil version for avatars.
- `hero_prompt` / `icon_prompt` (TextField) — stored prompts used for generation to allow re-rendering.
- `generator_version` (CharField) — track which prompt-template/model version created the assets.
- `status` (CharField choices: draft, generating, live, needs_regen, archived).
- `created_at` / `updated_at` timestamps.

## Notes
- JSON fields allow us to preserve ordered descriptors without creating numerous relational tables; we can normalize later if needed.
- ManyToMany to `TriggerTopic` ensures safety alignment with user preferences.
- `status` keeps UI informed about render progress and enables background tasks to retry.
- Accessibility notes become the alt text/source for audio descriptions.
- Future extension: version history table so regenerations don’t overwrite past appearances.
