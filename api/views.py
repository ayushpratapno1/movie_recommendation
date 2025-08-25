from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from movies.models import Movie
from users.models import Rating, Watchlist

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
