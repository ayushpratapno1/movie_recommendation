from django.core.management.base import BaseCommand
from movies.models import Movie, Genre, Person
from django.db import transaction

class Command(BaseCommand):
    help = 'Populate database with popular movies like Netflix/Amazon'
    
    def handle(self, *args, **options):
        self.stdout.write('🎬 Populating database with popular movies...')
        
        # Create genres first
        genres_data = [
            'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 
            'Music', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western'
        ]
        
        for genre_name in genres_data:
            Genre.objects.get_or_create(name=genre_name)
        
        self.stdout.write('✅ Created genres')
        
        # Popular movies data (like Netflix/Amazon catalog)
        movies_data = [
            # Action Movies
            {
                'title': 'The Dark Knight',
                'plot': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
                'release_year': 2008,
                'duration_minutes': 152,
                'genres': ['Action', 'Crime', 'Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
                'average_rating': 4.8
            },
            {
                'title': 'Avengers: Endgame',
                'plot': 'After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos\' actions and restore balance to the universe.',
                'release_year': 2019,
                'duration_minutes': 181,
                'genres': ['Action', 'Adventure', 'Sci-Fi'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg',
                'average_rating': 4.7
            },
            {
                'title': 'John Wick',
                'plot': 'An ex-hit-man comes out of retirement to track down the gangsters that took everything from him.',
                'release_year': 2014,
                'duration_minutes': 101,
                'genres': ['Action', 'Crime', 'Thriller'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg',
                'average_rating': 4.5
            },
            {
                'title': 'Mad Max: Fury Road',
                'plot': 'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.',
                'release_year': 2015,
                'duration_minutes': 120,
                'genres': ['Action', 'Adventure', 'Sci-Fi'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/hA2ple9q4qnwxp3hKVNhroipsir.jpg',
                'average_rating': 4.6
            },
            
            # Comedy Movies
            {
                'title': 'The Grand Budapest Hotel',
                'plot': 'A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy in the hotel\'s glorious years under an exceptional concierge.',
                'release_year': 2014,
                'duration_minutes': 99,
                'genres': ['Comedy', 'Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg',
                'average_rating': 4.4
            },
            {
                'title': 'Superbad',
                'plot': 'Two co-dependent high school seniors are forced to deal with separation anxiety after their plan to stage a booze-soaked party goes awry.',
                'release_year': 2007,
                'duration_minutes': 113,
                'genres': ['Comedy'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg',
                'average_rating': 4.2
            },
            {
                'title': 'Parasite',
                'plot': 'A poor family schemes to become employed by a wealthy family by infiltrating their household and posing as unrelated, highly qualified individuals.',
                'release_year': 2019,
                'duration_minutes': 132,
                'genres': ['Comedy', 'Drama', 'Thriller'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',
                'average_rating': 4.8
            },
            
            # Drama Movies
            {
                'title': 'The Shawshank Redemption',
                'plot': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'release_year': 1994,
                'duration_minutes': 142,
                'genres': ['Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
                'average_rating': 4.9
            },
            {
                'title': 'Forrest Gump',
                'plot': 'The presidencies of Kennedy and Johnson, Vietnam, Watergate, and other history unfold through the perspective of an Alabama man with an IQ of 75.',
                'release_year': 1994,
                'duration_minutes': 142,
                'genres': ['Drama', 'Romance'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
                'average_rating': 4.7
            },
            {
                'title': 'The Godfather',
                'plot': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
                'release_year': 1972,
                'duration_minutes': 175,
                'genres': ['Crime', 'Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
                'average_rating': 4.9
            },
            
            # Sci-Fi Movies
            {
                'title': 'Inception',
                'plot': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'release_year': 2010,
                'duration_minutes': 148,
                'genres': ['Action', 'Sci-Fi', 'Thriller'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
                'average_rating': 4.8
            },
            {
                'title': 'Interstellar',
                'plot': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
                'release_year': 2014,
                'duration_minutes': 169,
                'genres': ['Adventure', 'Drama', 'Sci-Fi'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
                'average_rating': 4.6
            },
            {
                'title': 'The Matrix',
                'plot': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
                'release_year': 1999,
                'duration_minutes': 136,
                'genres': ['Action', 'Sci-Fi'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
                'average_rating': 4.7
            },
            
            # Horror Movies
            {
                'title': 'Get Out',
                'plot': 'A young African-American visits his white girlfriend\'s parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point.',
                'release_year': 2017,
                'duration_minutes': 104,
                'genres': ['Horror', 'Mystery', 'Thriller'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg',
                'average_rating': 4.3
            },
            {
                'title': 'A Quiet Place',
                'plot': 'In a post-apocalyptic world, a family is forced to live in silence while hiding from monsters with ultra-sensitive hearing.',
                'release_year': 2018,
                'duration_minutes': 90,
                'genres': ['Drama', 'Horror', 'Sci-Fi'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg',
                'average_rating': 4.4
            },
            
            # Romance Movies
            {
                'title': 'La La Land',
                'plot': 'A jazz musician and an aspiring actress meet and fall in love in Los Angeles while pursuing their dreams.',
                'release_year': 2016,
                'duration_minutes': 128,
                'genres': ['Comedy', 'Drama', 'Music', 'Romance'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg',
                'average_rating': 4.3
            },
            {
                'title': 'The Notebook',
                'plot': 'A poor yet passionate young man falls in love with a rich young woman, giving her a sense of freedom, but they are soon separated because of their social differences.',
                'release_year': 2004,
                'duration_minutes': 123,
                'genres': ['Drama', 'Romance'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/qom1SZSENdmHFNZBXbtJAU0WTlC.jpg',
                'average_rating': 4.2
            },
            
            # Animation Movies
            {
                'title': 'Spider-Man: Into the Spider-Verse',
                'plot': 'Teen Miles Morales becomes Spider-Man of his reality, crossing his path with five counterparts from other dimensions to stop a threat for all realities.',
                'release_year': 2018,
                'duration_minutes': 117,
                'genres': ['Animation', 'Action', 'Adventure'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg',
                'average_rating': 4.6
            },
            {
                'title': 'Toy Story 4',
                'plot': 'When a new toy called "Forky" joins Woody and the gang, a road trip alongside old and new friends reveals how big the world can be for a toy.',
                'release_year': 2019,
                'duration_minutes': 100,
                'genres': ['Animation', 'Adventure', 'Comedy', 'Family'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg',
                'average_rating': 4.4
            },
            
            # More Popular Movies
            {
                'title': 'Pulp Fiction',
                'plot': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.',
                'release_year': 1994,
                'duration_minutes': 154,
                'genres': ['Crime', 'Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
                'average_rating': 4.8
            },
            {
                'title': 'Fight Club',
                'plot': 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.',
                'release_year': 1999,
                'duration_minutes': 139,
                'genres': ['Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/bptfVGEQuv6vDTIMVCHjJ9Dz8PX.jpg',
                'average_rating': 4.7
            },
            {
                'title': 'The Wolf of Wall Street',
                'plot': 'Based on the true story of Jordan Belfort, from his rise to a wealthy stock-broker living the high life to his fall involving crime, corruption and the federal government.',
                'release_year': 2013,
                'duration_minutes': 180,
                'genres': ['Biography', 'Comedy', 'Crime', 'Drama'],
                'poster_url': 'https://image.tmdb.org/t/p/w500/34m2tygAYBGqA9MXKhRDtzYd4MR.jpg',
                'average_rating': 4.5
            },
        ]
        
        created_count = 0
        
        with transaction.atomic():
            for movie_data in movies_data:
                # Check if movie already exists
                movie, created = Movie.objects.get_or_create(
                    title=movie_data['title'],
                    release_year=movie_data['release_year'],
                    defaults={
                        'plot': movie_data['plot'],
                        'duration_minutes': movie_data['duration_minutes'],
                        'poster_url': movie_data['poster_url'],
                        'average_rating': movie_data['average_rating']
                    }
                )
                
                if created:
                    # Add genres
                    for genre_name in movie_data['genres']:
                        genre = Genre.objects.get(name=genre_name)
                        movie.genres.add(genre)
                    
                    created_count += 1
                    self.stdout.write(f'✅ Created: {movie.title}')
                else:
                    self.stdout.write(f'⚠️  Already exists: {movie.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully added {created_count} popular movies to the database!'
            )
        )
        
        # Show stats
        total_movies = Movie.objects.count()
        total_genres = Genre.objects.count()
        
        self.stdout.write(f'\n📊 Database Statistics:')
        self.stdout.write(f'   🎬 Total Movies: {total_movies}')
        self.stdout.write(f'   🎭 Total Genres: {total_genres}')
        
        self.stdout.write(f'\n🚀 Your home page will now be filled with popular movies!')
        self.stdout.write(f'   Visit http://localhost:8000/ to see the updated recommendations!')
