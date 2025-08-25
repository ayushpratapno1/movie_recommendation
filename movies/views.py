from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Movie, Genre
from users.models import Rating, Watchlist

def home(request):
    # Get movies for different carousels
    trending_movies = Movie.objects.all()[:10]  # Simple trending for now
    recommended_movies = []
    
    if request.user.is_authenticated:
        # Get user's rated movies for recommendations (basic logic)
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
    
    genres = Genre.objects.all()
    
    context = {
        'trending_movies': trending_movies,
        'recommended_movies': recommended_movies,
        'genres': genres,
    }
    return render(request, 'movies/home.html', context)

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    user_rating = None
    in_watchlist = False
    
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, movie=movie).rating
        except Rating.DoesNotExist:
            pass
        
        in_watchlist = Watchlist.objects.filter(user=request.user, movie=movie).exists()
    
    # Similar movies (same genre)
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

def search(request):
    query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    year_filter = request.GET.get('year', '')
    
    movies = Movie.objects.all()
    
    if query:
        movies = movies.filter(
            Q(title__icontains=query) | 
            Q(plot__icontains=query) |
            Q(cast__name__icontains=query) |
            Q(directors__name__icontains=query)
        ).distinct()
    
    if genre_filter:
        movies = movies.filter(genres__name=genre_filter)
    
    if year_filter:
        movies = movies.filter(release_year=year_filter)
    
    context = {
        'movies': movies,
        'query': query,
        'genres': Genre.objects.all(),
        'selected_genre': genre_filter,
        'selected_year': year_filter,
    }
    return render(request, 'movies/search.html', context)

def genre_movies(request, genre_name):
    genre = get_object_or_404(Genre, name=genre_name)
    movies = Movie.objects.filter(genres=genre)
    
    context = {
        'genre': genre,
        'movies': movies,
    }
    return render(request, 'movies/genre_movies.html', context)
