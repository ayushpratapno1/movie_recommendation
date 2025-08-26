from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

import json

from movies.models import Movie
from users.models import Rating, Watchlist
from users.preference_service import RealTimePreferenceService

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
    """Rate a movie"""
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        rating_value = data.get('rating')
        
        if not movie_id or not rating_value:
            return JsonResponse({'error': 'Missing movie_id or rating'}, status=400)
        
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Create or update rating
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': rating_value}
        )
        
        return JsonResponse({
            'success': True,
            'rating': rating.rating,
            'created': created
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        
        deleted_count, _ = Watchlist.objects.filter(
            user=request.user,
            movie=movie
        ).delete()
        
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
