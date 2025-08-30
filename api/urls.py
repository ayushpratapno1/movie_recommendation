from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('rate/', views.rate_movie, name='rate_movie'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),
    
    # Real-time recommendation endpoints
    path('track/', views.track_interaction, name='track_interaction'),
    path('realtime-recommendations/', views.get_realtime_recommendations, name='realtime_recommendations'),
    path('dynamic-carousels/', views.get_dynamic_carousels, name='dynamic_carousels'),
    path('user-insights/', views.get_user_insights, name='user_insights'),
    path('refresh/', views.refresh_recommendations, name='refresh_recommendations'),
    path('hybrid-recommendations/', views.get_hybrid_recommendations, name='hybrid_recommendations'),
    path('ncf-similar/<int:movie_id>/', views.get_ncf_similar_movies, name='ncf_similar_movies'),
]
