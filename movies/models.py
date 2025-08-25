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
    genres = models.ManyToManyField(Genre, related_name='movies')
    cast = models.ManyToManyField(Person, related_name='acted_movies', blank=True)
    directors = models.ManyToManyField(Person, related_name='directed_movies', blank=True)
    average_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.release_year})"

class MovieTag(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)  # e.g., 'feel-good', 'dark', 'plot-twist'
    
    class Meta:
        unique_together = ['movie', 'tag']
