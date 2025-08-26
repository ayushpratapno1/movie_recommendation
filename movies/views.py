from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from .models import Movie, Genre
from users.models import Rating, Watchlist, UserPreference, UserInteraction
from users.preference_service import RealTimePreferenceService
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

def index(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('movies:home')
    return render(request, 'movies/index.html')

def home(request):
    """Dynamic homepage with real-time personalization"""
    if not request.user.is_authenticated:
        return redirect('movies:index')
        
    context = {}
    
    # Track homepage visit
    # This visit itself is an interaction
    session_id = request.session.session_key or request.session.create()
    
    # Get user preferences
    try:
        user_pref = UserPreference.objects.get(user=request.user)
        user_pref.apply_time_decay()
        preferred_genres = user_pref.get_preferred_genres(top_n=5)
    except UserPreference.DoesNotExist:
        preferred_genres = []
    
    # **Personalized Recommendations** (Main section)
    personalized_movies = RealTimePreferenceService.get_personalized_recommendations(
        request.user, limit=10
    )
    
    # **Dynamic Genre Carousels** - Based on real-time preferences
    genre_carousels = RealTimePreferenceService.get_dynamic_genre_carousels(
        request.user, max_genres=3
    )
    
    context.update({
        'personalized_movies': personalized_movies,
        'genre_carousels': genre_carousels,
        'user_preferred_genres': preferred_genres
        })
    
    # **Multiple Movie Sections like Netflix/Amazon**
    
    # 1. Trending Movies (based on interactions and ratings)
    trending_movies = Movie.objects.annotate(
        interaction_count=Count('userinteraction')
    ).order_by('-interaction_count', '-average_rating')[:12]
    
    # 2. Top Rated Movies (highest average rating) - Ensure all have ratings
    top_rated_movies = Movie.objects.exclude(
        average_rating=0.0
    ).order_by('-average_rating', '-release_year')[:12]
    
    # 3. Recently Added Movies
    recent_movies = Movie.objects.order_by('-created_at')[:12]
    
    # 4. Popular by Genre sections
    popular_genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror', 'Romance']
    genre_sections = []
    
    for genre_name in popular_genres:
        try:
            genre = Genre.objects.get(name=genre_name)
            genre_movies = Movie.objects.filter(
                genres=genre
            ).order_by('-average_rating', '-release_year')[:8]
            
            if genre_movies.exists():
                genre_sections.append({
                    'title': f'Popular {genre_name} Movies',
                    'movies': list(genre_movies),
                    'genre': genre_name.lower()
                })
        except Genre.DoesNotExist:
            continue
    
    # 5. Decade-based sections
    decade_sections = []
    decades = [
        (2020, 2024, '2020s'),
        (2010, 2019, '2010s'), 
        (2000, 2009, '2000s'),
        (1990, 1999, '90s Classics')
    ]
    
    for start_year, end_year, decade_name in decades:
        decade_movies = Movie.objects.filter(
            release_year__gte=start_year,
            release_year__lte=end_year
        ).order_by('-average_rating')[:8]
        
        if decade_movies.exists():
            decade_sections.append({
                'title': f'Best of {decade_name}',
                'movies': list(decade_movies),
                'decade': decade_name.lower()
            })
    
    # **All Genres** for browse
    genres = Genre.objects.all()
    
    context.update({
        'trending_movies': trending_movies,
        'top_rated_movies': top_rated_movies,
        'recent_movies': recent_movies,
        'genre_sections': genre_sections,
        'decade_sections': decade_sections,
        'genres': genres,
    })
    
    return render(request, 'movies/home.html', context)

def movie_detail(request, movie_id):
    """Movie detail with interaction tracking"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    # **Track this interaction immediately**
    if request.user.is_authenticated:
        RealTimePreferenceService.track_interaction(
            user=request.user,
            movie=movie,
            interaction_type='view_detail',
            context={'page': 'detail', 'session_id': request.session.session_key}
        )
    
    # Get user-specific data
    user_rating = None
    in_watchlist = False
    
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, movie=movie).rating
        except Rating.DoesNotExist:
            pass
        
        in_watchlist = Watchlist.objects.filter(user=request.user, movie=movie).exists()
    
        # **Smart Similar Movies** - based on user's current preferences
    if request.user.is_authenticated:
        all_personalized = RealTimePreferenceService.get_personalized_recommendations(
            request.user, limit=10
        )
        # Filter out the current movie from the list
        similar_movies = [m for m in all_personalized if m.id != movie.id][:6]
    else:
        similar_movies = Movie.objects.filter(
            genres__in=movie.genres.all()
        ).exclude(id=movie.id).distinct()[:6]
    
    context = {
        'movie': movie,
        'user_rating': user_rating,
        'in_watchlist': in_watchlist,
        'similar_movies': similar_movies,
    }
    return render(request, 'movies/movie_detail.html', context)

# AJAX endpoint for tracking clicks
@login_required
def track_movie_click(request):
    """Track when user clicks on a movie"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            movie_id = data.get('movie_id')
            source = data.get('source', 'unknown')  # 'trending', 'recommended', 'genre'
            
            movie = get_object_or_404(Movie, id=movie_id)
            
            RealTimePreferenceService.track_interaction(
                user=request.user,
                movie=movie,
                interaction_type='recommendation_click' if 'recommend' in source else 'click',
                context={
                    'page': 'home',
                    'source': source,
                    'session_id': request.session.session_key
                }
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def search(request):
    """Search movies by title"""
    query = request.GET.get('q', '')
    movies = []
    
    if query:
        movies = Movie.objects.filter(
            title__icontains=query
        ).select_related().prefetch_related('genres')[:20]
    
    context = {
        'movies': movies,
        'query': query,
    }
    return render(request, 'movies/search.html', context)

def genre_movies(request, genre_name):
    """Show movies by genre"""
    try:
        genre = Genre.objects.get(name=genre_name)
        movies = Movie.objects.filter(
            genres=genre
        ).select_related().prefetch_related('genres')[:50]
        
        context = {
            'movies': movies,
            'genre': genre,
        }
        return render(request, 'movies/genre_movies.html', context)
    except Genre.DoesNotExist:
        return render(request, 'movies/genre_movies.html', {
            'movies': [],
            'genre': {'name': genre_name},
            'error': f'Genre "{genre_name}" not found.'
        })
