from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import Movie, Genre, Person
from users.models import UserProfile, Rating, Watchlist

class Command(BaseCommand):
    help = 'Populate database with sample data'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Genres
        genres_data = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller", "Romance", "Horror"]
        for genre_name in genres_data:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            if created:
                self.stdout.write(f'Created genre: {genre_name}')
        
        # Create Persons
        persons_data = [
            {"name": "Leonardo DiCaprio", "primary_role": "actor"},
            {"name": "Christopher Nolan", "primary_role": "director"},
            {"name": "Scarlett Johansson", "primary_role": "actor"},
            {"name": "Martin Scorsese", "primary_role": "director"},
            {"name": "Christian Bale", "primary_role": "actor"},
            {"name": "Marion Cotillard", "primary_role": "actor"},
        ]
        
        for person_data in persons_data:
            person, created = Person.objects.get_or_create(
                name=person_data["name"], 
                defaults={"primary_role": person_data["primary_role"]}
            )
            if created:
                self.stdout.write(f'Created person: {person_data["name"]}')
        
        # Create Movies
        movies_data = [
            {
                "title": "Inception",
                "plot": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "release_year": 2010,
                "duration_minutes": 148,
                "genres": ["Sci-Fi", "Thriller"],
                "directors": ["Christopher Nolan"],
                "cast": ["Leonardo DiCaprio", "Marion Cotillard"]
            },
            {
                "title": "The Wolf of Wall Street", 
                "plot": "Based on the true story of Jordan Belfort, from his rise to a wealthy stock-broker living the high life to his fall involving crime, corruption and the federal government.",
                "release_year": 2013,
                "duration_minutes": 180,
                "genres": ["Drama", "Comedy"],
                "directors": ["Martin Scorsese"],
                "cast": ["Leonardo DiCaprio"]
            },
            {
                "title": "The Dark Knight",
                "plot": "Batman faces the Joker in this epic superhero thriller.",
                "release_year": 2008,
                "duration_minutes": 152,
                "genres": ["Action", "Drama"],
                "directors": ["Christopher Nolan"],
                "cast": ["Christian Bale"]
            }
        ]
        
        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=movie_data["title"],
                defaults={
                    "plot": movie_data["plot"],
                    "release_year": movie_data["release_year"],
                    "duration_minutes": movie_data["duration_minutes"]
                }
            )
            
            if created:
                # Add genres
                for genre_name in movie_data["genres"]:
                    genre = Genre.objects.get(name=genre_name)
                    movie.genres.add(genre)
                
                # Add directors
                for director_name in movie_data["directors"]:
                    director = Person.objects.get(name=director_name)
                    movie.directors.add(director)
                
                # Add cast
                for actor_name in movie_data["cast"]:
                    actor = Person.objects.get(name=actor_name)
                    movie.cast.add(actor)
                
                movie.save()
                self.stdout.write(f'Created movie: {movie_data["title"]}')
        
        # Create sample user profile (if user exists)
        try:
            user = User.objects.get(username='ayush')
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profile.favorite_genres.set(Genre.objects.filter(name__in=["Sci-Fi", "Drama"]))
                profile.preferred_decade = "2010s"
                profile.dark_mode = True
                profile.save()
                self.stdout.write('Created user profile')
            
            # Add sample ratings
            inception = Movie.objects.get(title="Inception")
            rating, created = Rating.objects.get_or_create(
                user=user, 
                movie=inception,
                defaults={"rating": 5}
            )
            if created:
                self.stdout.write('Added sample rating')
            
            # Add to watchlist
            dark_knight = Movie.objects.get(title="The Dark Knight")
            watchlist_item, created = Watchlist.objects.get_or_create(
                user=user, 
                movie=dark_knight
            )
            if created:
                self.stdout.write('Added movie to watchlist')
                
        except User.DoesNotExist:
            self.stdout.write('User "ayush" not found. Skipping user-specific data.')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
