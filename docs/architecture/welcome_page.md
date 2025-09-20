# Welcome Page Blueprint

## Goals
- Offer a joyful, inclusive landing experience before authentication.
- Surface login/register flows and tease the TMDb-powered universe with a random queer film card.
- Present an initial overlay (“prelude”) with a bold welcome message that sets tone: humorous, affirming, a bit shady.

## Flow
1. Visitor hits `/`.
2. Full-screen overlay fades in with welcome copy + “Enter the Qwirverse” button.
3. On dismiss, the main page shows two panes:
   - **Left:** Authentication module (tabs for login / register or two cards with buttons).
   - **Right:** Featured random film card, drawing from TMDb keyword `Queer`.
4. Refresh button on film card fetches another title via AJAX.

## Content Tone
- Inclusive, modern, celebratory, slightly mischievous.
- Example overlay text:
  > “Hey glitter comet. Welcome to Qwir Blingz — the galaxy where trans futures, sex worker brilliance, disabled joy, and every misfit glow-up gets the front row. Come in, hydrate, and let's get you orbiting.”

## Components
- Overlay component with Tailwind classes (loaded via CDN for now).
- Main layout uses CSS grid: left column (form), right column (film card).
- Film card shows poster, title/original title, country, language, production year, director credits, cast snippet, synopsis, rating, and TMDb/IMDb links when available.

## Backend Pieces
- Django view `WelcomeView` (class-based) renders template.
- Utilizes `tmdb.services.sample_movie_by_keyword` with fallback caching.
- AJAX endpoint `/api/teasers/queer-film/` returns JSON for random film; uses Django REST Framework.

## Front-end Logic
- Inline JS handles overlay dismiss (stores `sessionStorage` flag so returning visitors skip).
- JS fetch call to refresh film.

## Next Steps
- Implement view, DRF endpoint, template, and static assets.
- Add tests for view context + API response.
- Hook into existing TMDb client, with graceful handling when API key missing.
