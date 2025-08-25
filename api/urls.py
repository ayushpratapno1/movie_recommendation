from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('rate/', views.rate_movie, name='rate_movie'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),
]
