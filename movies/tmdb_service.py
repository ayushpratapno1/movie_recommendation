"""
TMDb (The Movie Database) API service for fetching movie data and posters
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TMDbService:
    """Service for interacting with The Movie Database API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  # Your API key from the code
    
    @classmethod
    def search_movie(cls, title, year=None):
        """Search for a movie by title and optional year"""
        # Check if TMDb API is enabled
        if not getattr(settings, 'TMDB_API_ENABLED', False):
            logger.debug(f"TMDb API disabled, skipping search for '{title}'")
            return None
            
        try:
            params = {
                'api_key': cls.API_KEY,
                'query': title,
                'language': 'en-US'
            }
            
            if year:
                params['year'] = year
            
            response = requests.get(f"{cls.BASE_URL}/search/movie", params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                return results[0]  # Return the first (most relevant) result
            
        except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
            logger.debug(f"TMDb API unavailable for movie '{title}': {e}")
        except Exception as e:
            logger.warning(f"Unexpected error searching for movie '{title}': {e}")
        
        return None
    
    @classmethod
    def get_movie_details(cls, tmdb_id):
        """Get detailed movie information by TMDb ID"""
        # Check if TMDb API is enabled
        if not getattr(settings, 'TMDB_API_ENABLED', False):
            logger.debug(f"TMDb API disabled, skipping details for ID '{tmdb_id}'")
            return None
            
        try:
            params = {
                'api_key': cls.API_KEY,
                'language': 'en-US'
            }
            
            response = requests.get(f"{cls.BASE_URL}/movie/{tmdb_id}", params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching movie details for ID {tmdb_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching movie details for ID {tmdb_id}: {e}")
        
        return None
    
    @classmethod
    def get_poster_url(cls, tmdb_id=None, poster_path=None):
        """Get full poster URL from TMDb ID or poster path"""
        # Check if TMDb API is enabled (only for API calls, not for building URLs)
        if tmdb_id and not getattr(settings, 'TMDB_API_ENABLED', False):
            logger.debug(f"TMDb API disabled, skipping poster fetch for ID '{tmdb_id}'")
            return None
            
        try:
            if poster_path:
                # If we already have the poster path, just build the full URL
                return f"{cls.IMAGE_BASE_URL}{poster_path}"
            
            if tmdb_id:
                # Fetch movie details to get poster path
                movie_data = cls.get_movie_details(tmdb_id)
                if movie_data and movie_data.get('poster_path'):
                    return f"{cls.IMAGE_BASE_URL}{movie_data['poster_path']}"
            
        except Exception as e:
            logger.error(f"Error getting poster URL: {e}")
        
        return None
    
    @classmethod
    def find_movie_poster(cls, title, year=None):
        """Find and return poster URL for a movie by title and year"""
        try:
            # Search for the movie
            movie_data = cls.search_movie(title, year)
            
            if movie_data and movie_data.get('poster_path'):
                return f"{cls.IMAGE_BASE_URL}{movie_data['poster_path']}"
            
        except Exception as e:
            logger.error(f"Error finding poster for '{title}' ({year}): {e}")
        
        return None
    
    @classmethod
    def get_movie_backdrop(cls, tmdb_id):
        """Get backdrop/banner image URL"""
        try:
            movie_data = cls.get_movie_details(tmdb_id)
            if movie_data and movie_data.get('backdrop_path'):
                return f"https://image.tmdb.org/t/p/w1280{movie_data['backdrop_path']}"
        except Exception as e:
            logger.error(f"Error getting backdrop for ID {tmdb_id}: {e}")
        
        return None


def update_movie_posters():
    """
    Utility function to update existing movies with TMDb posters
    Run this as a management command or in Django shell
    """
    from .models import Movie
    
    updated_count = 0
    total_movies = Movie.objects.count()
    
    print(f"Updating posters for {total_movies} movies...")
    
    for i, movie in enumerate(Movie.objects.all(), 1):
        print(f"Processing {i}/{total_movies}: {movie.title}")
        
        # Skip if movie already has a poster
        if movie.poster_url and movie.poster_url.startswith('http'):
            continue
        
        # Try to find poster
        poster_url = TMDbService.find_movie_poster(movie.title, movie.release_year)
        
        if poster_url:
            movie.poster_url = poster_url
            movie.save()
            updated_count += 1
            print(f"  ✓ Updated poster for {movie.title}")
        else:
            print(f"  ✗ No poster found for {movie.title}")
    
    print(f"Updated {updated_count} movie posters!")
    return updated_count
