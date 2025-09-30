# Configuration du Feed LGBT - Qwir Blingz

## ✅ Statut d'implémentation

Le feed LGBT avec carousels thématiques est maintenant **entièrement implémenté** et fonctionnel !

## 📋 Thématiques disponibles

Les 15 thématiques suivantes sont configurées et prêtes :

1. **Transidentités** (`trans-joy`) - Films et séries centrés sur les expériences et les joies trans
2. **Lesbiennes** (`lesbian-love`) - Histoires lesbiennes, romances, drames, docs et plus
3. **Gays** (`gay-celebration`) - Créations gays : pride, mémoire, fêtes, luttes et amours
4. **Queers** (`queer-joy`) - Panorama queer : joyeuses galaxies, club kids, ballrooms, résistance
5. **LGBTQIA+** (`lgbt-history`) - Archives et imaginaires LGBTQIA+ intergénérationnels
6. **Non-binaire** (`non-binary`) - Identités non-binaires, fluides et genderqueer à l'écran
7. **Théories du Genre** (`gender-studies`) - Essais, docs et fictions qui bousculent les cadres du genre
8. **Féminisme radical** (`radical-feminism`) - Héritages et combats transféministes décoloniaux
9. **Intersex** (`intersex`) - Récits intersexes : lutte, douceur et autodétermination
10. **Asexuel** (`asexual`) - Narrations ace et aromantiques, des contes aux docs
11. **Travail du sexe** (`tds-sex-work`) - Travail du sexe, mutual aid, luttes anti-répression
12. **Bi** (`bisexual`) - Identités bisexuelles, pansexuelles et plurisexuelles à l'écran
13. **Pan** (`pansexual`) - Narrations pansexuelles et polyromantiques, amours sans frontières
14. **Joies handies** (`disability-joy`) - Récits handis, mad pride, neurodivergence et fierté crip
15. **LGBTQ+ racisé·es** (`bipoc-lgbtq`) - Expériences LGBTQ+ racisées, décoloniales et intersectionnelles

## 🚀 Pour tester

1. Démarrer le serveur :
   ```bash
   cd backend
   uv run manage.py runserver
   ```

2. Se connecter avec :
   - **Username**: `admin`
   - **Password**: `admin123`

3. Aller sur le feed : `http://localhost:8000/feed/`

## 🎨 Fonctionnalités

- **Carousels horizontaux** avec défilement fluide
- **Cartes de films** interactives avec posters
- **Modal détaillé** pour chaque film (clic sur une carte)
- **Boutons de rafraîchissement** par thématique ou global
- **Design responsive** optimisé mobile/desktop
- **Fallbacks** avec contenu de secours si TMDb indisponible
- **Intégration TMDb** pour contenu dynamique

## 🔧 API Endpoints

- `GET /feed/` - Page principale du feed
- `POST /api/feed/carousels/{slug}/` - Rafraîchir un carousel spécifique
- `GET /feed/themes/{slug}/` - Page détaillée d'une thématique

## 📂 Architecture

- **Templates** : `templates/frontend/feed.html`
- **Services** : `backend/frontend/services.py`
- **Modèles** : `backend/media_catalog/models.py` (IdentityTag, MediaItem, MediaList)
- **API** : `backend/frontend/api.py`
- **URLs** : `backend/frontend/urls.py`

Le système est entièrement opérationnel et prêt pour la production !