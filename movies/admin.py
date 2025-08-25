from django.contrib import admin
from .models import Movie, Genre, Person, MovieTag

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'average_rating']
    list_filter = ['release_year', 'genres']
    search_fields = ['title']
    filter_horizontal = ['genres', 'cast', 'directors']

admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(MovieTag)
