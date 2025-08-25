from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Watchlist, Rating

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
    user_ratings = Rating.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'profile': profile,
        'user_ratings': user_ratings,
    }
    return render(request, 'users/profile.html', context)

@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'watchlist_items': watchlist_items,
    }
    return render(request, 'users/watchlist.html', context)
