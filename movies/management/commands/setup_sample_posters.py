from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = 'Setup sample movie posters without API calls'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up sample movie posters...')
        
        # Sample poster URLs for popular movies (these are real TMDb URLs)
        sample_posters = {
            'The Dark Knight': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
            'Avatar': 'https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg',
            'Inception': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
            'The Matrix': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
            'Interstellar': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
            'The Wolf of Wall Street': 'https://image.tmdb.org/t/p/w500/34m2tygAYBGqA9MXKhRDtzYd4MR.jpg',
            'Pulp Fiction': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
            'The Godfather': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
            'Forrest Gump': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
            'The Shawshank Redemption': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
        }
        
        updated_count = 0
        
        for title, poster_url in sample_posters.items():
            try:
                movies = Movie.objects.filter(title__icontains=title)
                for movie in movies:
                    if not movie.poster_url or movie.poster_url == '':
                        movie.poster_url = poster_url
                        movie.save(update_fields=['poster_url'])
                        updated_count += 1
                        self.stdout.write(f'✅ Updated poster for: {movie.title}')
            except Movie.DoesNotExist:
                continue
        
        # For test movies, set them to empty string to avoid API calls
        test_movies = Movie.objects.filter(title__startswith='Test ')
        for movie in test_movies:
            if movie.poster_url is None:
                movie.poster_url = ''
                movie.save(update_fields=['poster_url'])
                self.stdout.write(f'⚠️  Marked test movie as no poster: {movie.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} movie posters'
            )
        )
        
        if updated_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    'No movies found to update. Make sure you have movies in your database.'
                )
            )
