from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.contrib import messages
from .models import UserProfile, Watchlist, Rating
from movies.models import Genre, Movie

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('movies:home')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle profile updates
    if request.method == 'POST':
        # Update favorite genres
        selected_genres = request.POST.getlist('favorite_genres')
        profile.favorite_genres.set(Genre.objects.filter(id__in=selected_genres))
        
        # Update preferred decade
        preferred_decade = request.POST.get('preferred_decade')
        if preferred_decade:
            profile.preferred_decade = preferred_decade
        
        # Update dark mode preference
        profile.dark_mode = 'dark_mode' in request.POST
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    # Get user statistics
    user_ratings = Rating.objects.filter(user=request.user).order_by('-created_at')
    watchlist_items = Watchlist.objects.filter(user=request.user).order_by('-added_at')
    
    # Calculate statistics
    total_ratings = user_ratings.count()
    average_rating = user_ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Top rated movies by user
    top_rated_movies = user_ratings.filter(rating__gte=4).select_related('movie')[:5]
    
    # Recently rated movies
    recent_ratings = user_ratings.select_related('movie')[:10]
    
    # Watchlist count
    watchlist_count = watchlist_items.count()
    
    # Favorite genres statistics - simplified approach
    genre_stats = []
    if user_ratings.exists():
        genre_data = {}
        for rating in user_ratings.select_related('movie').prefetch_related('movie__genres'):
            for genre in rating.movie.genres.all():
                if genre.name not in genre_data:
                    genre_data[genre.name] = {'count': 0, 'total_rating': 0}
                genre_data[genre.name]['count'] += 1
                genre_data[genre.name]['total_rating'] += rating.rating
        
        for genre_name, data in genre_data.items():
            genre_stats.append({
                'movie__genres__name': genre_name,
                'count': data['count'],
                'avg_rating': round(data['total_rating'] / data['count'], 1)
            })
        
        genre_stats = sorted(genre_stats, key=lambda x: x['count'], reverse=True)[:5]
    
    # Movies by decade - using a safer approach
    decade_stats = []
    if user_ratings.exists():
        # Get all ratings with movie data
        ratings_with_movies = user_ratings.select_related('movie')
        decade_data = {}
        
        for rating in ratings_with_movies:
            decade = f"{(rating.movie.release_year // 10) * 10}s"
            if decade not in decade_data:
                decade_data[decade] = {'count': 0, 'total_rating': 0}
            decade_data[decade]['count'] += 1
            decade_data[decade]['total_rating'] += rating.rating
        
        # Calculate averages and sort
        for decade, data in decade_data.items():
            decade_stats.append({
                'decade': decade,
                'count': data['count'],
                'avg_rating': round(data['total_rating'] / data['count'], 1)
            })
        
        decade_stats = sorted(decade_stats, key=lambda x: x['count'], reverse=True)
    
    # All genres for the form
    all_genres = Genre.objects.all().order_by('name')
    
    context = {
        'profile': profile,
        'user_ratings': recent_ratings,
        'watchlist_items': watchlist_items[:5],  # Show recent 5
        'total_ratings': total_ratings,
        'average_rating': round(average_rating, 1) if average_rating else 0,
        'top_rated_movies': top_rated_movies,
        'watchlist_count': watchlist_count,
        'genre_stats': genre_stats,
        'decade_stats': decade_stats,
        'all_genres': all_genres,
    }
    return render(request, 'users/profile.html', context)

@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'watchlist_items': watchlist_items,
    }
    return render(request, 'users/watchlist.html', context)

def logout_view(request):
    """Custom logout view that redirects to home page"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('movies:home')
