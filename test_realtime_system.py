#!/usr/bin/env python
"""
Test script for Real-time Recommendation System
Run this to test the system functionality
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recsys.settings')
django.setup()

from django.contrib.auth.models import User
from movies.models import Movie, Genre
from users.preference_service import RealTimePreferenceService
from users.models import UserPreference, UserInteraction
import json

def test_realtime_system():
    print("🎬 Testing Real-time Movie Recommendation System")
    print("=" * 50)
    
    # Create test user if doesn't exist
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    if created:
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Create test movies and genres if needed
    action_genre, _ = Genre.objects.get_or_create(name='Action')
    comedy_genre, _ = Genre.objects.get_or_create(name='Comedy')
    drama_genre, _ = Genre.objects.get_or_create(name='Drama')
    
    # Create test movies
    movies_data = [
        {'title': 'Test Action Movie', 'genre': action_genre, 'year': 2023},
        {'title': 'Test Comedy Movie', 'genre': comedy_genre, 'year': 2023},
        {'title': 'Test Drama Movie', 'genre': drama_genre, 'year': 2023},
    ]
    
    test_movies = []
    for movie_data in movies_data:
        movie, created = Movie.objects.get_or_create(
            title=movie_data['title'],
            defaults={
                'plot': f'A great {movie_data["genre"].name.lower()} movie',
                'release_year': movie_data['year'],
                'duration_minutes': 120
            }
        )
        movie.genres.add(movie_data['genre'])
        test_movies.append(movie)
    
    print("✅ Test movies created/found")
    
    # Test 1: Track interactions and see preference changes
    print("\n🧪 Test 1: Tracking User Interactions")
    print("-" * 30)
    
    # Initial preferences
    initial_insights = RealTimePreferenceService.get_user_insights(user)
    print(f"Initial preferences: {initial_insights.get('genre_preferences', {})}")
    
    # Simulate user interactions
    interactions = [
        (test_movies[0], 'click', None),
        (test_movies[0], 'rate', 5),  # Love action movies
        (test_movies[1], 'click', None),
        (test_movies[1], 'rate', 2),  # Don't like comedy
        (test_movies[0], 'watchlist_add', None),  # Add action to watchlist
    ]
    
    for movie, interaction_type, rating in interactions:
        context = {'page': 'test', 'source': 'test_script'}
        result = RealTimePreferenceService.track_interaction(
            user=user,
            movie=movie,
            interaction_type=interaction_type,
            rating_value=rating,
            context=context
        )
        print(f"✅ Tracked: {interaction_type} for {movie.title} (rating: {rating})")
    
    # Check updated preferences
    updated_insights = RealTimePreferenceService.get_user_insights(user)
    print(f"Updated preferences: {updated_insights.get('genre_preferences', {})}")
    
    # Test 2: Get personalized recommendations
    print("\n🧪 Test 2: Personalized Recommendations")
    print("-" * 30)
    
    recommendations = RealTimePreferenceService.get_personalized_recommendations(
        user=user,
        limit=5,
        use_cache=False
    )
    
    print(f"Got {len(recommendations)} personalized recommendations:")
    for i, movie in enumerate(recommendations, 1):
        genres = [g.name for g in movie.genres.all()]
        print(f"  {i}. {movie.title} ({', '.join(genres)})")
    
    # Test 3: Dynamic genre carousels
    print("\n🧪 Test 3: Dynamic Genre Carousels")
    print("-" * 30)
    
    carousels = RealTimePreferenceService.get_dynamic_genre_carousels(
        user=user,
        max_genres=3
    )
    
    print(f"Generated {len(carousels)} genre carousels:")
    for carousel in carousels:
        print(f"  📺 {carousel['title']}")
        print(f"     {carousel['subtitle']}")
        print(f"     Movies: {len(carousel['movies'])}")
    
    # Test 4: User insights
    print("\n🧪 Test 4: User Behavior Insights")
    print("-" * 30)
    
    insights = RealTimePreferenceService.get_user_insights(user)
    print("User Insights:")
    print(f"  👤 User ID: {insights['user_id']}")
    print(f"  ⭐ Average Rating: {insights['average_rating']}")
    print(f"  📊 Total Ratings: {insights['total_ratings']}")
    print(f"  🎯 Engagement Score: {insights['engagement_score']}")
    print(f"  🎭 Preference Diversity: {insights['preference_diversity']}")
    print(f"  🔄 Recent Interactions: {insights['recent_interactions']}")
    
    # Test 5: AI Training Data Export
    print("\n🧪 Test 5: AI Training Data Preparation")
    print("-" * 30)
    
    training_data = RealTimePreferenceService.prepare_ai_training_data(user_limit=5)
    print(f"Prepared training data for {len(training_data)} users")
    
    if training_data:
        sample_user = training_data[0]
        print("Sample user data structure:")
        for key, value in sample_user.items():
            if isinstance(value, dict):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
    
    print("\n🎉 All tests completed successfully!")
    print("\nReal-time recommendation system is working! 🚀")
    print("\nNext steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Visit http://localhost:8000/ and interact with movies")
    print("3. Watch recommendations update in real-time!")
    print("4. Export training data: python manage.py export_training_data")
    print("5. Integrate your AI model using ai_model_integration_example.py")

if __name__ == '__main__':
    try:
        test_realtime_system()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
