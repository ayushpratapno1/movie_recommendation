from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie, Genre
from django.utils import timezone
import json

class UserPreference(models.Model):
    """Track dynamic user preferences in real-time"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Genre preferences with weights (0.0 to 1.0)
    genre_preferences = models.JSONField(default=dict)  # {"Sci-Fi": 0.8, "Action": 0.6}
    
    # Recent interaction patterns
    recent_genre_interactions = models.JSONField(default=list)  # Last 50 interactions
    last_updated = models.DateTimeField(auto_now=True)
    
    # Preference decay settings
    base_preference_weight = models.FloatField(default=0.5)
    interaction_boost = models.FloatField(default=0.1)  # How much each interaction boosts preference
    decay_rate = models.FloatField(default=0.95)  # Daily decay multiplier
    
    def update_genre_preference(self, genre_name, interaction_type='view', boost_factor=1.0):
        """Update genre preference based on user interaction"""
        if not self.genre_preferences:
            self.genre_preferences = {}
        
        # Get current preference or start with base weight
        current_pref = self.genre_preferences.get(genre_name, self.base_preference_weight)
        
        # Calculate boost based on interaction type
        interaction_boosts = {
            'view': 0.05,
            'rate_high': 0.15,  # 4-5 star rating
            'rate_low': -0.1,   # 1-2 star rating
            'watchlist_add': 0.1,
            'watchlist_remove': -0.05,
            'click': 0.03
        }
        
        boost = interaction_boosts.get(interaction_type, 0.05) * boost_factor
        new_preference = min(1.0, max(0.0, current_pref + boost))
        
        self.genre_preferences[genre_name] = new_preference
        
        # Track recent interactions (keep last 50)
        if not self.recent_genre_interactions:
            self.recent_genre_interactions = []
        
        self.recent_genre_interactions.append({
            'genre': genre_name,
            'interaction': interaction_type,
            'timestamp': timezone.now().isoformat(),
            'boost': boost
        })
        
        # Keep only last 50 interactions
        if len(self.recent_genre_interactions) > 50:
            self.recent_genre_interactions = self.recent_genre_interactions[-50:]
        
        self.save()
        return new_preference
    
    def get_preferred_genres(self, top_n=5):
        """Get top N preferred genres"""
        if not self.genre_preferences:
            return []
        
        sorted_genres = sorted(
            self.genre_preferences.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [genre for genre, weight in sorted_genres[:top_n] if weight > 0.3]
    
    def apply_time_decay(self):
        """Apply time-based decay to preferences"""
        if not self.genre_preferences:
            return
        
        # Calculate days since last update
        days_since_update = (timezone.now() - self.last_updated).days
        if days_since_update > 0:
            decay_factor = self.decay_rate ** days_since_update
            
            for genre in self.genre_preferences:
                # Decay towards base weight, not zero
                current = self.genre_preferences[genre]
                self.genre_preferences[genre] = (
                    self.base_preference_weight + 
                    (current - self.base_preference_weight) * decay_factor
                )
            
            self.save()

class UserInteraction(models.Model):
    """Enhanced interaction tracking for real-time adaptation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    interaction_choices = [
        ('click', 'Clicked Movie'),
        ('view_detail', 'Viewed Detail Page'),
        ('rate', 'Rated Movie'),
        ('watchlist_add', 'Added to Watchlist'),
        ('watchlist_remove', 'Removed from Watchlist'),
        ('search', 'Found via Search'),
        ('recommendation_click', 'Clicked Recommendation'),
    ]
    
    interaction_type = models.CharField(max_length=20, choices=interaction_choices)
    rating_value = models.IntegerField(null=True, blank=True)  # If interaction is rating
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Context information
    page_context = models.CharField(max_length=50, null=True, blank=True)  # 'home', 'search', 'detail'
    recommendation_source = models.CharField(max_length=50, null=True, blank=True)  # 'trending', 'genre', 'collaborative'
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['movie', 'interaction_type']),
        ]

class Rating(models.Model):
    """Movie ratings by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/5"

class Watchlist(models.Model):
    """User's watchlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
    
    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.movie.title}"