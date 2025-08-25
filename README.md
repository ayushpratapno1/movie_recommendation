Movie Recommendation System (Django)

A production-style web app that recommends movies using a hybrid approach (content-based + collaborative signals), built with Django, HTML/CSS/JS, and a pretrained model hosted on Hugging Face. The system supports user accounts, ratings, watchlists, search/filters, and explainable recommendations suitable for a college project and demo deployment.

Features
Personalized recommendations via a hybrid engine (content embeddings + user ratings) with “Why this movie?” explanations.

User accounts: sign up, login/logout, profiles, preferences, watch history.

Ratings and feedback: 1–5 stars, like/dislike, “not interested” to refine recommendations.

Watchlist: add/remove titles and view saved items.

Search and filters: title, genre, year, cast, tags/moods.

Responsive UI with carousels/grids similar to OTT layouts.

Admin panel: manage movies, tags, and data.

Optional AI chat assistant for natural-language suggestions via a cost‑friendly LLM API.

Tech Stack
Backend: Django, Django REST Framework (for APIs).

ML/RecSys: Python, scikit‑learn or Surprise/implicit; transformer embeddings (Hugging Face).

Frontend: Django templates, HTML, CSS, vanilla JS.

Data: MovieLens/TMDb (for demo/training).

Background jobs (optional): Celery + Redis for batch training/inference.

Hosting model: Hugging Face Hub (load by repo id/token).

Deployment targets: any Django-friendly host (Railway/Render/AWS/Heroku).

Architecture

Django app modules:

core: settings, auth, admin.

movies: models (Movie, Genre, Tag, Person), ingestion commands.

users: profiles, preferences, ratings, watchlists.

recommender: pipelines to compute embeddings, similarity, and top‑N recommendations; Hugging Face model loader.

api: REST endpoints for recommendations, search, rating, watchlist.

web: template views for pages (Home, Detail, Watchlist, Profile).

Data flow:

Ingest dataset → 2) Preprocess features/embeddings → 3) Train/fine‑tune model in Colab → 4) Push model to Hugging Face → 5) Django loads model at startup → 6) API serves recs to UI.

Getting Started

Prerequisites

Python 3.10+ and pip/venv.

Git.

Optional: Redis (for Celery) and a Hugging Face token if loading a private model.

Installation

Clone repository

git clone <your-repo-url> && cd movie-recsys

Create and activate virtual env

python -m venv .venv && source .venv/bin/activate # Windows: .venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Environment variables (.env)

DJANGO_SECRET_KEY=your_secret

DEBUG=true

DATABASE_URL=sqlite:///db.sqlite3 # or Postgres URL

HF_TOKEN=your_hf_token_if_private

HF_MODEL_REPO=org/model-repo-id

Run migrations and seed sample data

python manage.py migrate

python manage.py loaddata seed.json # or custom load command

Start server

python manage.py runserver

Quick Start (Demo Data)

Use provided fixture or management command to load a small MovieLens/TMDb subset.

Visit http://127.0.0.1:8000, register a user, rate a few movies, and open the Home page to see recommendations populate.

Usage

Home: personalized carousels (Trending, For You, Because You Liked, By Genre).

Movie detail: poster, synopsis, cast, similar movies, and explanation (“Because you liked X”).

Search: query by title/people; filter by genre, year, tags/moods.

Watchlist: add/remove titles; manage saved items.

Profile: edit preferences; see rating history.

Admin: add/edit movies, tags, cast.

Recommendation Engine

Approach: hybrid of content similarity (text/image embeddings over plots/posters) and collaborative signals (user–item ratings).

Training:

Use Colab to compute embeddings and train CF/implicit model; export artifacts.

Push model/embeddings to Hugging Face.

Serving:

Django loads embeddings/model on startup or via lazy loader; computes top‑N per user with fallbacks for cold‑start (popularity, genre).

Batch vs. realtime:

Optional Celery tasks to refresh similarity matrices and cached recommendations nightly/hourly.

API Endpoints

GET /api/recommendations/ → top‑N for current user.

GET /api/search/?q=&genre=&year=&tag= → results with filters.

POST /api/rate/ {movie_id, rating} → update model signals.

POST /api/watchlist/add|remove {movie_id} → manage list. 

GET /api/me/ → profile preferences and stats.

Data Sources

MovieLens ratings and metadata for experimentation.

TMDb for posters and extended fields (respect API TOS).

Environment & Configuration

Settings split for dev/prod; DEBUG=false in production.

Database: SQLite for dev; Postgres recommended for prod.

Static/media handling configured via WhiteNoise or cloud storage in prod.

Hugging Face:

HF_MODEL_REPO for model name; HF_TOKEN if private; caching enabled.

Deployment

Collect static: python manage.py collectstatic.

Run with a WSGI/ASGI server (gunicorn/uvicorn) behind a reverse proxy.

Provision environment variables and persistent database/storage on host (Railway/Render/AWS/Heroku).

Add a worker (optional) for Celery tasks with Redis.

Screenshots / Demo

Include GIFs or images of Home, Movie Detail, Watchlist, and Admin UI to showcase flows and UX.

Optional: link to a deployed demo instance.

Roadmap

Cold‑start improvements via onboarding quiz and short explicit preference capture.

Better explanations with natural‑language templates.

Chat assistant for natural language discovery (e.g., “feel‑good sci‑fi from the 90s”).

A/B testing of ranking strategies and UI variants.

Contributing