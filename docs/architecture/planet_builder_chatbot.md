# Planet Builder Chatbot Blueprint

## Goals
- Offer a guided conversation that collects all attributes needed for `PlanetAppearance` while feeling playful and affirming.
- Allow members to skip, revisit, or randomize options without losing previously shared info.
- Produce a structured payload that can be converted into prompts + saved to the model, then queued for image generation.

## Conversation Structure
Each turn collects a themed cluster of attributes. The chatbot keeps a running state (per session) with:
- `planet_id` or temporary draft identifier
- current step index
- collected attributes dictionary (maps to `PlanetAppearance` fields)
- skipped fields list for optional prompts
- confirmation flags (e.g., palette confirmed)

### Steps
1. **Introduction**
   - Welcome message, explain purpose.
   - Ask for planet display `name` and optional `tagline`/`motto`.
2. **Identity & Tone**
   - Gather `emotional_tone` (with curated list + free form) and `accessibility_notes` seed.
   - Optionally capture story beat (origin snippet) that feeds `origin_type`.
3. **Color Palette**
   - Offer color suggestions (predefined or random) and allow custom HEX entry.
   - Collect `primary_color`, `secondary_color`, additional swatches appended to `palette`.
4. **Surface & Texture**
   - Pick `surface_type` from quick list (gas, rocky, etc.).
   - Ask for descriptors (“glossy, mossy, embroidered”) → `surface_descriptors` array.
5. **Rings & Satellites**
   - Inquire about ring preference (`ring_style`, descriptors, color) and moons (`has_moons`, `moon_count`, descriptors).
6. **Atmosphere & Sky**
   - Choose `atmosphere_style` (aurora, nebula, etc.) and descriptors for patterns, weather, lighting.
7. **Materials & Origin**
   - Determine `origin_type` (natural, crafted, reclaimed, etc.).
   - Capture `materials` array with free-form strings.
8. **Safety & Accessibility**
   - Prompt for `accessibility_notes` detailing sensory cues.
   - Offer selection of `TriggerTopic` tags to avoid (tie into user prefs); collect `custom_trigger_warnings` free text.
9. **Summary & Confirmation**
   - Present a bulleted recap.
   - Allow edits per section, randomization, or acceptance.
10. **Generation Kickoff**
    - On confirmation, mark status `generating`, construct prompts (`hero_prompt`, `icon_prompt`), enqueue task.

## State Machine Design
- Represent steps as enums or constants; config stored as JSON/YAML for adjustability.
- Each step has:
  - `id`, `title`, `prompt_template`
  - `input_type` (choice, free_text, multi_select, color_picker)
  - `validation` rules (regex for HEX, min/max counts)
  - `field_mapping` detailing target model field(s)
  - `dependencies` (e.g., skip ring questions if `ring_style == none`)
- Transitions triggered by user intent: `next`, `previous`, `randomize`, `skip`, `edit(step_id)`.

## Prompt Generation Skeleton
- Build base descriptors from collected attributes (e.g., combine surface + materials + atmosphere into one descriptive paragraph).
- Maintain prompt templates in a versioned module (reference stored in `generator_version`).
- Provide fallback prompts when fields missing (use curated defaults).

## API Integration
- Expose endpoints (or websocket) for the front-end wizard:
  - `POST /planets/<id>/builder/start`
  - `POST /planets/<id>/builder/step` (payload: user message / form data)
  - `POST /planets/<id>/builder/confirm`
  - `POST /planets/<id>/builder/randomize/<step>`
- Authentication ensures only the owner works on their planet.

## Storage
- Draft state persisted in a dedicated model or cached within Redis keyed by session.
- On each step completion, upsert into `PlanetAppearance` (status `draft`).
- Maintain conversation log for transparency; strip sensitive data before logging.

## Open Questions
- Should we support collaborative planet building (multiple members)?
- How do we handle mid-flight changes after generation (version history)?
- Where will image generation run (local diffusion vs managed service)?
