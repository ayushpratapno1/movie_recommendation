Movie Recommendation System (Django)

Overview
This project solves “what should I watch next?” by delivering personalized, real‑time movie recommendations. It learns from user behavior instantly (clicks, ratings, watchlist actions, page views), blends content signals (genres, year) and popularity, and provides robust fallbacks for cold‑start users. The goal is a production‑style, demo‑ready app with a Netflix‑like UI.

Key Features
- Personalized, real‑time recommendations that adapt after every interaction
- Login/Signup; Profile with editable preferences and statistics
- Ratings (1–5 stars) with persistent UI; Watchlist add/remove
- Search, Genre pages, Similar movies
- Rich Home UI (carousels), dynamic genre sections, trending/top rated/recent
- TMDb posters integration with caching and fallback behavior
- Secure APIs with CSRF; production‑minded settings toggles
- Optional AI training/export for advanced hybrid recommendations

Tech Stack
- Backend: Django, Django REST Framework
- Frontend: Django templates, HTML, CSS (Bootstrap), vanilla JS
- ML/RecSys: Python, scikit‑learn (optional), feature export for training
- Data: TMDb (posters), your catalog via management commands
- Optional: Celery/Redis for batch jobs; Hugging Face for model hosting

Architecture (What Runs Where)
- movie_recsys/settings.py: Security flags, static files, TMDb keys, auth redirects
- movies/models.py: Movie, Genre, tmdb_id, Movie.get_poster_url() with caching/fallbacks
- movies/views.py: index, home, movie_detail, search, genre_movies, click tracking
- movies/tmdb_service.py: Safe TMDb fetches (timeouts, error handling, enable flag)
- movies/management/commands/: populate_popular_movies, smart_movie_discovery, setup_sample_posters
- users/models.py: UserPreference (JSONField + time‑decay), Rating, Watchlist, UserInteraction
- users/preference_service.py: Real‑time learning and recommendation logic
- users/views.py: Signup, logout, profile (stats + editable preferences)
- api/urls.py, api/views.py: Endpoints for tracking, recommendations, carousels, insights
- templates/: base, home, movie_detail, index (landing), profile, macros
- static/: JS for real‑time updates and enhanced UI; CSS for modern cards and carousels
- ai_model_integration_example.py: Optional RandomForest pipeline for advanced hybrid

Getting Started

Prerequisites

Python 3.10+ and pip/venv.

Git.

Optional: Redis (for Celery) and a Hugging Face token if loading a private model.

Installation

Clone repository

git clone <your-repo-url> && cd movie-recsys

Create and activate virtual env

python -m venv venv
# Windows
venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Environment variables (example)

DJANGO_SECRET_KEY=your_secret
DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost
TMDB_API_ENABLED=true
TMDB_API_KEY=your_tmdb_key

Run migrations and seed sample data

python manage.py migrate
python manage.py populate_popular_movies
python manage.py setup_sample_posters   # optional if TMDb disabled

Start server

python manage.py runserver

Quick Start
- Visit http://127.0.0.1:8000
- Register a user, rate a few movies, add to watchlist
- Open Home to see recommendations adapt in real‑time

Usage
- Home: personalized carousels (Trending, For You, By Genre, Decades)
- Movie detail: poster, synopsis, similar movies, star ratings (persist visually)
- Search: query by title; Genre pages; Watchlist management
- Profile: edit preferences; see stats and recent activity

How Recommendations Work (Strategies)
1) Real‑time preference learning (primary)
   - Tracks interactions (click, view_detail, add/remove_watchlist, rate)
   - Updates per‑genre weights with time‑decay; caches user vectors
   - Produces personalized lists and dynamic genre carousels
2) Content‑based filtering
   - Uses genres and release_year to build genre/decade sections
3) Popularity/trending
   - Orders by interaction counts and average_rating for robust fallbacks
4) Collaborative/user‑based (utility jobs)
   - Finds similar users by preference overlap and surfaces their favorites

Concrete examples from code
- Personalized and dynamic sections (movies/views.py):
```python
from django.db.models import Count
personalized = RealTimePreferenceService.get_personalized_recommendations(request.user, limit=10)
dynamic = RealTimePreferenceService.get_dynamic_genre_carousels(request.user, max_genres=3)
trending = Movie.objects.annotate(interaction_count=Count('userinteraction')).order_by('-interaction_count','-average_rating')[:12]
top_rated = Movie.objects.exclude(average_rating=0.0).order_by('-average_rating','-release_year')[:12]
```
- Similar movies (movie_detail):
```python
all_personalized = RealTimePreferenceService.get_personalized_recommendations(request.user, limit=10)
similar_movies = [m for m in all_personalized if m.id != movie.id][:6]
```
- Posters (models.py):
```python
url = movie.get_poster_url()  # caches results; respects TMDB_API_ENABLED
```

API (selected)
- POST /api/track/ → record interaction { movie_id, interaction_type, context }
- GET  /api/realtime/recommendations/ → personalized list
- GET  /api/realtime/carousels/ → dynamic genre carousels
- GET  /api/realtime/insights/ → user analytics
- POST /api/refresh/ → refresh sections server‑side

Data & Posters
- TMDb for posters; enable via TMDB_API_ENABLED and TMDB_API_KEY
- `setup_sample_posters` command to bypass TMDb in development

Environment & Configuration
- DEBUG/SECRET_KEY/ALLOWED_HOSTS from env; secure cookies/HSTS toggles for prod
- Static files configured; CSRF protected APIs

Deployment
- python manage.py collectstatic
- Run with WSGI/ASGI server behind a reverse proxy

Demo Walkthrough
1) Sign up and log in
2) Visit Home → Trending/Top Rated + initial Personalized
3) Click/rate a few titles → Home adapts within seconds
4) Open a movie → similar titles leverage your current profile
5) Profile → view stats and edit preferences

AI Model (optional advanced)
- Code: ai_model_integration_example.py (RandomForest example)
- Export: users/management/commands/export_training_data.py
- Train: prepare features, fit, save with joblib; optionally push to Hugging Face
- Integrate: load model and score candidates alongside real‑time layer

Troubleshooting
- CSRF/405: include X‑CSRFToken header; custom logout view supports GET
- Posters missing: enable TMDb or run setup_sample_posters; check timeouts
- “sklearn could not be resolved”: activate venv; pip install -r requirements.txt; set IDE interpreter
- DB errors: run makemigrations/migrate