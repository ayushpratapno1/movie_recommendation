from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),  # Landing page for non-authenticated users
    path('home/', views.home, name='home'),  # Main home page for authenticated users
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search, name='search'),
    path('genre/<str:genre_name>/', views.genre_movies, name='genre_movies'),
    path('track-click/', views.track_movie_click, name='track_click'),
]
