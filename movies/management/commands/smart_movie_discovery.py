from django.core.management.base import BaseCommand
from movies.models import Movie, Genre
from users.models import UserInteraction, UserPreference
from django.contrib.auth.models import User
from django.db.models import Count, Q
import random

class Command(BaseCommand):
    help = 'Automatically discover and add movies based on user behavior patterns'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Analyze specific user (optional)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be added without actually adding'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🤖 Smart Movie Discovery System')
        self.stdout.write('=' * 40)
        
        # Analyze user behavior patterns
        if options['user_id']:
            users = User.objects.filter(id=options['user_id'])
        else:
            # Get active users with interactions
            users = User.objects.filter(
                userinteraction__isnull=False
            ).distinct()[:10]  # Limit to 10 most active users
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No active users found'))
            return
        
        total_discovered = 0
        
        for user in users:
            discovered = self.discover_movies_for_user(user, options['dry_run'])
            total_discovered += discovered
            
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Smart discovery complete! '
                f'{"Would discover" if options["dry_run"] else "Discovered"} '
                f'{total_discovered} new movies'
            )
        )
    
    def discover_movies_for_user(self, user, dry_run=False):
        """Discover movies for a specific user based on their behavior"""
        
        self.stdout.write(f'\n👤 Analyzing user: {user.username}')
        
        # Get user's interaction patterns
        interactions = UserInteraction.objects.filter(user=user)
        
        # Analyze genre preferences
        genre_interactions = interactions.values('movie__genres__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        preferred_genres = []
        for item in genre_interactions[:3]:  # Top 3 genres
            if item['movie__genres__name']:
                preferred_genres.append(item['movie__genres__name'])
        
        if not preferred_genres:
            self.stdout.write('  ⚠️  No clear genre preferences found')
            return 0
        
        self.stdout.write(f'  🎭 Preferred genres: {", ".join(preferred_genres)}')
        
        # Discover movies based on patterns
        discovered_movies = []
        
        # 1. Similar movies from preferred genres
        for genre_name in preferred_genres:
            try:
                genre = Genre.objects.get(name=genre_name)
                
                # Find highly rated movies in this genre that user hasn't interacted with
                similar_movies = Movie.objects.filter(
                    genres=genre,
                    average_rating__gte=4.0
                ).exclude(
                    userinteraction__user=user
                ).order_by('-average_rating', '?')[:3]  # Random selection
                
                for movie in similar_movies:
                    if movie not in discovered_movies:
                        discovered_movies.append(movie)
                        
            except Genre.DoesNotExist:
                continue
        
        # 2. Movies liked by users with similar preferences
        similar_users = self.find_similar_users(user)
        for similar_user in similar_users[:2]:  # Top 2 similar users
            liked_movies = UserInteraction.objects.filter(
                user=similar_user,
                interaction_type='rate',
                rating_value__gte=4
            ).exclude(
                movie__userinteraction__user=user
            )[:2]
            
            for interaction in liked_movies:
                if interaction.movie not in discovered_movies:
                    discovered_movies.append(interaction.movie)
        
        # 3. Trending movies in preferred genres
        for genre_name in preferred_genres[:2]:
            try:
                genre = Genre.objects.get(name=genre_name)
                trending = Movie.objects.filter(
                    genres=genre
                ).annotate(
                    interaction_count=Count('userinteraction')
                ).exclude(
                    userinteraction__user=user
                ).order_by('-interaction_count', '-average_rating')[:2]
                
                for movie in trending:
                    if movie not in discovered_movies:
                        discovered_movies.append(movie)
                        
            except Genre.DoesNotExist:
                continue
        
        # Limit discoveries to avoid overwhelming
        discovered_movies = discovered_movies[:8]
        
        if not discovered_movies:
            self.stdout.write('  ℹ️  No new movies to discover')
            return 0
        
        self.stdout.write(f'  🔍 Discovered {len(discovered_movies)} movies:')
        
        for movie in discovered_movies:
            genres = [g.name for g in movie.genres.all()[:3]]
            self.stdout.write(
                f'    • {movie.title} ({movie.release_year}) - '
                f'{", ".join(genres)} - ⭐{movie.average_rating}'
            )
            
            if not dry_run:
                # Create a "discovery" interaction to mark this movie as suggested
                UserInteraction.objects.get_or_create(
                    user=user,
                    movie=movie,
                    interaction_type='recommendation_click',
                    defaults={
                        'page_context': 'smart_discovery',
                        'recommendation_source': 'ai_discovery'
                    }
                )
        
        return len(discovered_movies)
    
    def find_similar_users(self, target_user):
        """Find users with similar preferences"""
        
        # Get target user's genre preferences
        target_genres = set(
            UserInteraction.objects.filter(
                user=target_user
            ).values_list('movie__genres__name', flat=True)
        )
        
        if not target_genres:
            return User.objects.none()
        
        # Find users who like similar genres
        similar_users = []
        
        for user in User.objects.exclude(id=target_user.id):
            user_genres = set(
                UserInteraction.objects.filter(
                    user=user
                ).values_list('movie__genres__name', flat=True)
            )
            
            # Calculate genre overlap
            overlap = len(target_genres.intersection(user_genres))
            if overlap >= 2:  # At least 2 genres in common
                similar_users.append((user, overlap))
        
        # Sort by similarity and return top users
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return [user for user, _ in similar_users[:5]]
