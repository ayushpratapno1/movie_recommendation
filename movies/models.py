from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=200)
    role_choices = [
        ('actor', 'Actor'),
        ('director', 'Director'),
        ('writer', 'Writer'),
    ]
    primary_role = models.CharField(max_length=20, choices=role_choices)
    
    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    plot = models.TextField()
    release_year = models.IntegerField()
    duration_minutes = models.IntegerField()
    poster_url = models.URLField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True, help_text="The Movie Database ID for API calls")
    genres = models.ManyToManyField(Genre, related_name='movies')
    cast = models.ManyToManyField(Person, related_name='acted_movies', blank=True)
    directors = models.ManyToManyField(Person, related_name='directed_movies', blank=True)
    average_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_poster_url(self):
        """Get poster URL, fetching from TMDb if needed"""
        # Return cached URL if available
        if self.poster_url and self.poster_url.startswith('http'):
            return self.poster_url
        
        # If poster_url is explicitly set to empty string, don't retry API
        if self.poster_url == '':
            return None
        
        # Try to get from TMDb (only if we haven't tried before)
        if self.tmdb_id and self.poster_url is None:
            from .tmdb_service import TMDbService
            poster_url = TMDbService.get_poster_url(tmdb_id=self.tmdb_id)
            if poster_url:
                # Cache the URL in the database
                self.poster_url = poster_url
                self.save(update_fields=['poster_url'])
                return poster_url
            else:
                # Mark as attempted to avoid future API calls
                self.poster_url = ''
                self.save(update_fields=['poster_url'])
        
        # Try to search by title and year (only if we haven't tried before)
        elif self.poster_url is None:
            from .tmdb_service import TMDbService
            poster_url = TMDbService.find_movie_poster(self.title, self.release_year)
            if poster_url:
                # Cache the URL in the database
                self.poster_url = poster_url
                self.save(update_fields=['poster_url'])
                return poster_url
            else:
                # Mark as attempted to avoid future API calls
                self.poster_url = ''
                self.save(update_fields=['poster_url'])
        
        return None
    
    def __str__(self):
        return f"{self.title} ({self.release_year})"

class MovieTag(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)  # e.g., 'feel-good', 'dark', 'plot-twist'
    
    class Meta:
        unique_together = ['movie', 'tag']
