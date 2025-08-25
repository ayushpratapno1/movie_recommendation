from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search, name='search'),
    path('genre/<str:genre_name>/', views.genre_movies, name='genre_movies'),
]
