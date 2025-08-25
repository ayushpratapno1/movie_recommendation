from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie, Genre

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_genres = models.ManyToManyField(Genre, blank=True)
    preferred_decade_choices = [
        ('1990s', '1990s'),
        ('2000s', '2000s'),
        ('2010s', '2010s'),
        ('2020s', '2020s'),
    ]
    preferred_decade = models.CharField(max_length=10, choices=preferred_decade_choices, blank=True)
    dark_mode = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/5"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
    
    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.movie.title}"

class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    interaction_choices = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('not_interested', 'Not Interested'),
        ('watched', 'Watched'),
    ]
    interaction_type = models.CharField(max_length=20, choices=interaction_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie', 'interaction_type']
