"""
Django management command to update movie posters from TMDb API
Usage: python manage.py update_posters
"""
from django.core.management.base import BaseCommand
from movies.tmdb_service import update_movie_posters


class Command(BaseCommand):
    help = 'Update movie posters from The Movie Database (TMDb) API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of movies to update',
            default=None
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if movie already has a poster',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting movie poster update from TMDb API...')
        )
        
        try:
            updated_count = update_movie_posters()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} movie posters!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating posters: {e}')
            )
