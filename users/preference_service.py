from .models import UserPreference, UserInteraction, Rating
from .model_service import HybridModelService
from movies.models import Movie, Genre
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from django.core.cache import cache
import uuid
import json
import logging

logger = logging.getLogger(__name__)

class RealTimePreferenceService:
    """Enhanced service to handle real-time preference updates and AI-ready recommendations"""
    
    # Interaction weights for preference calculation
    INTERACTION_WEIGHTS = {
        'click': 0.1,
        'view_detail': 0.2,
        'watchlist_add': 0.4,
        'watchlist_remove': -0.2,
        'rate': 0.0,  # Will be calculated based on rating value
        'search': 0.1,
        'recommendation_click': 0.3,
    }
    @staticmethod
    def get_hybrid_recommendations(user, limit=20):
      """
      ENHANCED: Combine your real-time preferences with NCF predictions
      This is the heart of your upgraded recommendation system
      """
      # Determine strategy weights based on user engagement
      interaction_count = UserInteraction.objects.filter(user=user).count()
      # Determine strategy weights based on user engagement
      if interaction_count < 5:  # New users
        weights = {
            'ncf': 0.25,           # Limited collaborative data
            'realtime': 0.35,      # Your existing preference learning
            'content': 0.25,       # Genre-based recommendations
            'popularity': 0.15     # Safe popular choices
        }
      elif interaction_count < 50:  # Active users
        weights = {
            'ncf': 0.45,           # Strong collaborative patterns
            'realtime': 0.35,      # Your preference learning
            'content': 0.15,       # Genre diversity
            'popularity': 0.05     # Trending content
        }
      else:  # Power users
        weights = {
            'ncf': 0.50,           # Primary collaborative engine
            'realtime': 0.35,      # Your real-time insights
            'content': 0.10,       # Exploration
            'popularity': 0.05     # Serendipity
        }
    
      # Collect recommendations from each strategy
      recommendations_pool = {}
    
      # 1. Get NCF recommendations (your new world-class engine)
      if weights['ncf'] > 0:
        try:
            ncf_recs = HybridModelService.get_cached_ncf_recommendations(user, limit * 2)
            for i, movie in enumerate(ncf_recs):
                score = weights['ncf'] * (1.0 - i / len(ncf_recs)) if ncf_recs else 0
                recommendations_pool[movie.id] = recommendations_pool.get(movie.id, 0) + score
        except Exception as e:
            logger.warning(f"NCF recommendations failed: {e}")
    
      # 2. Get your existing real-time recommendations
      if weights['realtime'] > 0:
        try:
            realtime_recs = RealTimePreferenceService.get_personalized_recommendations(user, limit * 2)
            for i, movie in enumerate(realtime_recs):
                score = weights['realtime'] * (1.0 - i / len(realtime_recs)) if realtime_recs else 0
                recommendations_pool[movie.id] = recommendations_pool.get(movie.id, 0) + score
        except Exception as e:
            logger.warning(f"Realtime recommendations failed: {e}")
    
      # 3. Get content-based recommendations (FIXED LOGIC)
      if weights['content'] > 0:
        try:
            user_pref = UserPreference.objects.get(user=user)
            genre_preferences = user_pref.genre_preferences or {}
            if genre_preferences:
                content_recs = RealTimePreferenceService._get_weighted_recommendations(user, genre_preferences, limit)
                for i, movie in enumerate(content_recs):
                    score = weights['content'] * (1.0 - i / len(content_recs)) if content_recs else 0
                    recommendations_pool[movie.id] = recommendations_pool.get(movie.id, 0) + score
        except UserPreference.DoesNotExist:
            # Fallback to personalized recommendations if no preferences exist
            try:
                content_recs = RealTimePreferenceService.get_personalized_recommendations(user, limit)
                for i, movie in enumerate(content_recs):
                    score = weights['content'] * (1.0 - i / len(content_recs)) if content_recs else 0
                    recommendations_pool[movie.id] = recommendations_pool.get(movie.id, 0) + score
            except Exception as e:
                logger.warning(f"Content recommendations failed: {e}")
    
      # 4. Get popularity-based recommendations
      if weights['popularity'] > 0:
        try:
            popular_recs = RealTimePreferenceService._get_trending_movies(limit)
            for i, movie in enumerate(popular_recs):
                score = weights['popularity'] * (1.0 - i / len(popular_recs)) if popular_recs else 0
                recommendations_pool[movie.id] = recommendations_pool.get(movie.id, 0) + score
        except Exception as e:
            logger.warning(f"Popular recommendations failed: {e}")
    
      # Sort by combined score and return top recommendations
      if not recommendations_pool:
        # Ultimate fallback: return trending movies
        logger.warning("No recommendations generated from any strategy, falling back to trending")
        return RealTimePreferenceService._get_trending_movies(limit)
    
      sorted_recommendations = sorted(recommendations_pool.items(), key=lambda x: x[1], reverse=True)
    
      # Get Movie objects maintaining order
      final_movie_ids = [movie_id for movie_id, score in sorted_recommendations[:limit]]
      movies = Movie.objects.filter(id__in=final_movie_ids)
    
      # Maintain scoring order
      movie_dict = {movie.id: movie for movie in movies}
      final_movies = [movie_dict[movie_id] for movie_id in final_movie_ids if movie_id in movie_dict]
    
      return final_movies

    
    @staticmethod
    def get_cached_hybrid_recommendations(user, limit=20):
        """Cached version of hybrid recommendations"""
        cache_key = f"hybrid_recommendations_{user.id}_{limit}"
        cached = cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        recommendations = RealTimePreferenceService.get_hybrid_recommendations(user, limit)
        cache.set(cache_key, recommendations, 900)  # Cache for 15 minutes
        
        return recommendations

    @staticmethod
    def track_interaction(user, movie, interaction_type, rating_value=None, context=None):
        """Track user interaction and update preferences immediately"""
        if not user.is_authenticated:
            return None
        
        try:
            # Create interaction record
            interaction = UserInteraction.objects.create(
                user=user,
                movie=movie,
                interaction_type=interaction_type,
                rating_value=rating_value,
                page_context=context.get('page', '') if context else '',
                session_id=context.get('session_id', str(uuid.uuid4())) if context else '',
                recommendation_source=context.get('source', '') if context else ''
            )
            
            # Update user preferences in real-time
            user_pref, created = UserPreference.objects.get_or_create(user=user)
            
            # Calculate boost factor based on interaction type and rating
            boost_factor = RealTimePreferenceService._calculate_boost_factor(interaction_type, rating_value)
            
            # Update genre preferences based on the interaction
            for genre in movie.genres.all():
                user_pref.update_genre_preference(
                    genre.name, 
                    interaction_type, 
                    boost_factor
                )
            
            # Clear user's recommendation cache to force refresh
            cache_keys = [
                f"recommendations_{user.id}",
                f"personalized_movies_{user.id}",
                f"genre_carousels_{user.id}"
            ]
            for key in cache_keys:
                cache.delete(key)
            
            logger.info(f"Tracked interaction: {user.username} {interaction_type} {movie.title}")
            return interaction
            
        except Exception as e:
            logger.error(f"Error tracking interaction: {e}")
            return None
    
    @staticmethod
    def _calculate_boost_factor(interaction_type, rating_value=None):
        """Calculate boost factor based on interaction type and rating value"""
        base_weight = RealTimePreferenceService.INTERACTION_WEIGHTS.get(interaction_type, 0.1)
        
        if interaction_type == 'rate' and rating_value:
            # Rating-based boost: 1-2 stars = negative, 3 = neutral, 4-5 = positive
            if rating_value <= 2:
                return -0.3  # Negative preference
            elif rating_value == 3:
                return 0.1   # Slight positive
            else:  # 4-5 stars
                return 0.5 + (rating_value - 4) * 0.2  # 0.5 for 4 stars, 0.7 for 5 stars
        
        return base_weight
    
    @staticmethod
    def get_personalized_recommendations(user, limit=20, use_cache=True):
        """Get personalized recommendations based on current preferences with caching"""
        if not user.is_authenticated:
            return Movie.objects.all()[:limit]
        
        cache_key = f"personalized_movies_{user.id}_{limit}"
        
        if use_cache:
            cached_movies = cache.get(cache_key)
            if cached_movies:
                return cached_movies
        
        try:
            user_pref = UserPreference.objects.get(user=user)
            user_pref.apply_time_decay()  # Apply time decay
            
            # Get weighted genre preferences
            genre_preferences = user_pref.genre_preferences or {}
            
            if not genre_preferences:
                # Fallback to trending movies
                movies = RealTimePreferenceService._get_trending_movies(limit)
            else:
                movies = RealTimePreferenceService._get_weighted_recommendations(
                    user, genre_preferences, limit
                )
            
            # Cache for 5 minutes
            if use_cache:
                cache.set(cache_key, movies, 300)
            
            return movies
            
        except UserPreference.DoesNotExist:
            return RealTimePreferenceService._get_trending_movies(limit)
    
    @staticmethod
    def _get_weighted_recommendations(user, genre_preferences, limit):
        """Get recommendations weighted by genre preferences"""
        # Get movies from preferred genres, weighted by preference strength
        movie_scores = {}
        
        # Exclude already rated/watched movies
        excluded_ids = set(UserInteraction.objects.filter(
            user=user, 
            interaction_type__in=['rate', 'watchlist_add']
        ).values_list('movie_id', flat=True))
        
        for genre_name, preference_weight in genre_preferences.items():
            if preference_weight > 0.3:  # Only consider strong preferences
                try:
                    genre = Genre.objects.get(name=genre_name)
                    movies = Movie.objects.filter(
                        genres=genre
                    ).exclude(id__in=excluded_ids).select_related().prefetch_related('genres')
                    
                    for movie in movies:
                        if movie.id not in movie_scores:
                            movie_scores[movie.id] = {
                                'movie': movie,
                                'score': 0
                            }
                        # Add weighted score
                        movie_scores[movie.id]['score'] += preference_weight
                        
                except Genre.DoesNotExist:
                    continue
        
        # Sort by score and return top movies
        sorted_movies = sorted(
            movie_scores.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        return [item['movie'] for item in sorted_movies[:limit]]
    
    @staticmethod
    def _get_trending_movies(limit):
        """Get trending movies based on recent interactions"""
        return Movie.objects.annotate(
            interaction_count=Count('userinteraction', 
                filter=Q(userinteraction__timestamp__gte=timezone.now() - timezone.timedelta(days=7))
            )
        ).order_by('-interaction_count', '-average_rating')[:limit]
    
    @staticmethod
    def get_dynamic_genre_carousels(user, max_genres=3):
        """Get dynamic genre carousels based on user preferences"""
        if not user.is_authenticated:
            return []
        
        cache_key = f"genre_carousels_{user.id}"
        cached_carousels = cache.get(cache_key)
        if cached_carousels:
            return cached_carousels
        
        try:
            user_pref = UserPreference.objects.get(user=user)
            genre_preferences = user_pref.genre_preferences or {}
            
            carousels = []
            
            # Sort genres by preference weight
            sorted_genres = sorted(
                genre_preferences.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:max_genres]
            
            for genre_name, weight in sorted_genres:
                if weight > 0.4:  # Only show strong preferences
                    try:
                        genre = Genre.objects.get(name=genre_name)
                        
                        # Get movies from this genre, excluding already rated
                        movies = Movie.objects.filter(
                            genres=genre
                        ).exclude(
                            id__in=UserInteraction.objects.filter(
                                user=user, 
                                interaction_type='rate'
                            ).values_list('movie_id', flat=True)
                        ).select_related().prefetch_related('genres')[:8]
                        
                        if movies.exists():
                            carousels.append({
                                'title': f'More {genre_name} Movies for You',
                                'subtitle': f'Based on your preferences (Score: {weight:.1f})',
                                'movies': list(movies),
                                'genre': genre_name.lower(),
                                'weight': weight
                            })
                    except Genre.DoesNotExist:
                        continue
            
            # Cache for 10 minutes
            cache.set(cache_key, carousels, 600)
            return carousels
            
        except UserPreference.DoesNotExist:
            return []
    
    @staticmethod
    def get_user_insights(user):
        """Get user behavior insights for AI model training"""
        if not user.is_authenticated:
            return {}
        
        try:
            user_pref = UserPreference.objects.get(user=user)
            
            # Recent interactions analysis
            recent_interactions = UserInteraction.objects.filter(
                user=user,
                timestamp__gte=timezone.now() - timezone.timedelta(days=30)
            ).values('interaction_type').annotate(count=Count('id'))
            
            # Rating patterns
            ratings = Rating.objects.filter(user=user)
            avg_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
            
            # Genre distribution
            genre_distribution = {}
            for genre_name, weight in (user_pref.genre_preferences or {}).items():
                genre_distribution[genre_name] = weight
            
            return {
                'user_id': user.id,
                'genre_preferences': genre_distribution,
                'recent_interactions': {item['interaction_type']: item['count'] for item in recent_interactions},
                'average_rating': round(avg_rating, 2),
                'total_ratings': ratings.count(),
                'last_updated': user_pref.last_updated.isoformat() if user_pref.last_updated else None,
                'preference_diversity': len(genre_distribution),
                'engagement_score': sum(genre_distribution.values()) if genre_distribution else 0
            }
            
        except UserPreference.DoesNotExist:
            return {'user_id': user.id, 'new_user': True}
    
    @staticmethod
    def prepare_ai_training_data(user_limit=None):
        """Prepare data for AI model training"""
        users = User.objects.all()
        if user_limit:
            users = users[:user_limit]
        
        training_data = []
        for user in users:
            user_data = RealTimePreferenceService.get_user_insights(user)
            if not user_data.get('new_user', False):
                training_data.append(user_data)
        
        return training_data
    