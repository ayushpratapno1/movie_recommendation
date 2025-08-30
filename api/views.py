import logging
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from users.preference_service import RealTimePreferenceService
from users.model_service import HybridModelService
import json
from django.db import transaction, DatabaseError
import sqlite3
from django.core.cache import cache
import time

from movies.models import Movie
from users.models import Rating, Watchlist
from users.preference_service import RealTimePreferenceService

# Set up logger
logger = logging.getLogger(__name__)

@login_required
@require_GET
def get_hybrid_recommendations(request):
    """
    NEW: Enhanced recommendation endpoint using NCF + your existing system
    """
    try:
        limit = int(request.GET.get('limit', 20))
        
        # Get hybrid recommendations (NCF + your real-time system)
        movies = RealTimePreferenceService.get_cached_hybrid_recommendations(request.user, limit)
        
        movies_data = []
        for movie in movies:
            movies_data.append({
                'id': movie.id,
                'title': movie.title,
                'poster_url': movie.get_poster_url(),
                'average_rating': movie.average_rating,
                'source': 'hybrid_ncf',  # Identify as enhanced recommendations
                'genres': [genre.name for genre in movie.genres.all()],
                'release_year': movie.release_year
            })
        
        return JsonResponse({
            'status': 'success',
            'recommendations': movies_data,
            'count': len(movies_data),
            'method': 'hybrid_ncf_enhanced'
        })
        
    except Exception as e:
        logger.error(f"Hybrid recommendations error: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@login_required  
@require_GET
def get_ncf_similar_movies(request, movie_id):
    """
    NEW: Get similar movies using NCF model embeddings
    """
    try:
        # This would use your NCF model's learned embeddings
        # For now, fall back to your existing similarity
        movie = Movie.objects.get(id=movie_id)
        similar_movies = Movie.objects.filter(
            genres__in=movie.genres.all()
        ).exclude(id=movie_id).distinct()[:10]
        
        movies_data = [{
            'id': m.id,
            'title': m.title,
            'poster_url': m.get_poster_url(),
            'similarity_score': 0.85  # Placeholder - would come from NCF embeddings
        } for m in similar_movies]
        
        return JsonResponse({
            'status': 'success',
            'similar_movies': movies_data
        })
        
    except Movie.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

@login_required
def get_recommendations(request):
    """Get movie recommendations for the logged-in user"""
    # Simple recommendation logic for now
    user_ratings = Rating.objects.filter(user=request.user, rating__gte=4)
    
    if user_ratings.exists():
        # Get movies from same genres as highly rated ones
        liked_genres = []
        for rating in user_ratings:
            liked_genres.extend(rating.movie.genres.all())
        
        recommended_movies = Movie.objects.filter(
            genres__in=liked_genres
        ).exclude(
            id__in=[r.movie.id for r in user_ratings]
        ).distinct()[:10]
    else:
        # If no ratings, show trending movies
        recommended_movies = Movie.objects.all()[:10]
    
    movies_data = []
    for movie in recommended_movies:
        movies_data.append({
            'id': movie.id,
            'title': movie.title,
            'plot': movie.plot,
            'release_year': movie.release_year,
            'poster_url': movie.poster_url,
            'genres': [genre.name for genre in movie.genres.all()]
        })
    
    return JsonResponse({'recommendations': movies_data})

@login_required
@require_POST
def rate_movie(request):
    """Rate a movie with proper locking and debouncing"""
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        rating_value = data.get('rating')
        
        if not movie_id or not rating_value:
            return JsonResponse({'error': 'Missing movie_id or rating'}, status=400)
        
        # Validate rating value
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid rating value'}, status=400)
        
        # Create a unique lock key for this user-movie combination
        lock_key = f"rating_lock_{request.user.id}_{movie_id}"
        
        # Check if there's already a rating operation in progress
        if cache.get(lock_key):
            return JsonResponse({
                'error': 'Rating operation already in progress. Please wait.',
                'retry_after': 2
            }, status=429)
        
        # Set a lock for 5 seconds to prevent duplicate requests
        cache.set(lock_key, True, 5)
        
        try:
            # Use a retry mechanism for database locks
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with transaction.atomic():
                        movie = get_object_or_404(Movie, id=movie_id)
                        
                        # Create or update rating
                        rating, created = Rating.objects.update_or_create(
                            user=request.user,
                            movie=movie,
                            defaults={'rating': rating_value}
                        )
                        
                        # Update movie's average rating
                        update_movie_average_rating(movie)
                        
                        # Track the interaction for preference learning (only once)
                        RealTimePreferenceService.track_interaction(
                            user=request.user,
                            movie=movie,
                            interaction_type='rate',
                            rating_value=rating_value,
                            context={
                                'page': 'home',
                                'source': 'rating_api',
                                'session_id': request.session.session_key
                            }
                        )
                        
                        return JsonResponse({
                            'success': True,
                            'rating': rating.rating,
                            'created': created,
                            'message': 'Rating updated successfully' if not created else 'Rating added successfully'
                        })
                        
                except (DatabaseError, sqlite3.OperationalError) as e:
                    if 'database is locked' in str(e).lower() and retry_count < max_retries - 1:
                        retry_count += 1
                        time.sleep(0.1 * retry_count)  # Exponential backoff
                        continue
                    else:
                        raise e
                break
                
        finally:
            # Always release the lock
            cache.delete(lock_key)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in rate_movie: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def update_movie_average_rating(movie):
    """Update movie's average rating with error handling"""
    try:
        from django.db.models import Avg
        avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
        movie.average_rating = round(avg_rating, 1) if avg_rating else 0.0
        movie.save(update_fields=['average_rating'])
    except Exception as e:
        logger.error(f"Error updating movie average rating: {e}")

@login_required
@require_POST
def add_to_watchlist(request):
    """Add movie to user's watchlist"""
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        
        if not movie_id:
            return JsonResponse({'error': 'Missing movie_id'}, status=400)
        
        movie = get_object_or_404(Movie, id=movie_id)
        
        watchlist_item, created = Watchlist.objects.get_or_create(
            user=request.user,
            movie=movie
        )
        
        # Track the interaction for preference learning
        if created:  # Only track if actually added (not already in watchlist)
            RealTimePreferenceService.track_interaction(
                user=request.user,
                movie=movie,
                interaction_type='watchlist_add',
                context={
                    'page': 'home',
                    'source': 'watchlist_api',
                    'session_id': request.session.session_key
                }
            )
        
        return JsonResponse({
            'success': True,
            'added': created,
            'message': 'Added to watchlist' if created else 'Already in watchlist'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def remove_from_watchlist(request):
    """Remove movie from user's watchlist"""
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        
        if not movie_id:
            return JsonResponse({'error': 'Missing movie_id'}, status=400)
        
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Check if movie was in watchlist before deleting
        was_in_watchlist = Watchlist.objects.filter(
            user=request.user,
            movie=movie
        ).exists()
        
        deleted_count, _ = Watchlist.objects.filter(
            user=request.user,
            movie=movie
        ).delete()
        
        # Track the interaction for preference learning
        if was_in_watchlist:  # Only track if it was actually removed
            RealTimePreferenceService.track_interaction(
                user=request.user,
                movie=movie,
                interaction_type='watchlist_remove',
                context={
                    'page': 'home',
                    'source': 'watchlist_api',
                    'session_id': request.session.session_key
                }
            )
        
        return JsonResponse({
            'success': True,
            'removed': deleted_count > 0,
            'message': 'Removed from watchlist' if deleted_count > 0 else 'Not in watchlist'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Real-time recommendation endpoints

@login_required
@require_POST
def track_interaction(request):
    """Track user interaction and update preferences in real-time"""
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        interaction_type = data.get('interaction_type')
        rating_value = data.get('rating_value')
        context = data.get('context', {})
        
        if not movie_id or not interaction_type:
            return JsonResponse({'error': 'Missing movie_id or interaction_type'}, status=400)
        
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Track the interaction
        interaction = RealTimePreferenceService.track_interaction(
            user=request.user,
            movie=movie,
            interaction_type=interaction_type,
            rating_value=rating_value,
            context=context
        )
        
        if interaction:
            return JsonResponse({
                'success': True,
                'message': 'Interaction tracked successfully',
                'interaction_id': interaction.id
            })
        else:
            return JsonResponse({'error': 'Failed to track interaction'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_GET
def get_realtime_recommendations(request):
    """Get real-time personalized recommendations"""
    try:
        limit = int(request.GET.get('limit', 20))
        use_cache = request.GET.get('use_cache', 'true').lower() == 'true'
        
        # Get personalized recommendations
        movies = RealTimePreferenceService.get_personalized_recommendations(
            user=request.user,
            limit=limit,
            use_cache=use_cache
        )
        
        movies_data = []
        for movie in movies:
            movies_data.append({
                'id': movie.id,
                'title': movie.title,
                'plot': movie.plot[:200] + '...' if len(movie.plot) > 200 else movie.plot,
                'release_year': movie.release_year,
                'poster_url': movie.get_poster_url(),
                'genres': [genre.name for genre in movie.genres.all()],
                'average_rating': round(movie.average_rating, 1)
            })
        
        return JsonResponse({
            'success': True,
            'recommendations': movies_data,
            'count': len(movies_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_GET
def get_dynamic_carousels(request):
    """Get dynamic genre carousels based on user preferences"""
    try:
        max_genres = int(request.GET.get('max_genres', 3))
        
        carousels = RealTimePreferenceService.get_dynamic_genre_carousels(
            user=request.user,
            max_genres=max_genres
        )
        
        # Format carousel data for JSON response
        carousels_data = []
        for carousel in carousels:
            movies_data = []
            for movie in carousel['movies']:
                movies_data.append({
                    'id': movie.id,
                    'title': movie.title,
                    'release_year': movie.release_year,
                    'poster_url': movie.get_poster_url(),
                    'genres': [genre.name for genre in movie.genres.all()]
                })
            
            carousels_data.append({
                'title': carousel['title'],
                'subtitle': carousel['subtitle'],
                'genre': carousel['genre'],
                'weight': carousel['weight'],
                'movies': movies_data
            })
        
        return JsonResponse({
            'success': True,
            'carousels': carousels_data,
            'count': len(carousels_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_GET
def get_user_insights(request):
    """Get user behavior insights for debugging/analytics"""
    try:
        insights = RealTimePreferenceService.get_user_insights(request.user)
        return JsonResponse({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def refresh_recommendations(request):
    """Force refresh of user recommendations (clear cache)"""
    try:
        from django.core.cache import cache
        
        # Clear all user-specific caches
        cache_keys = [
            f"recommendations_{request.user.id}",
            f"personalized_movies_{request.user.id}",
            f"genre_carousels_{request.user.id}"
        ]
        
        for key in cache_keys:
            cache.delete(key)
        
        return JsonResponse({
            'success': True,
            'message': 'Recommendations refreshed successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
