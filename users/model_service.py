from django.core.cache import cache
from django.db.models import Q, Avg
from .models import User, Rating, UserInteraction
from movies.models import Movie
from ai_models.ncf_service import ncf_service
import logging

logger = logging.getLogger(__name__)

class HybridModelService:
    """
    Service to combine your existing recommendations with NCF predictions
    """
    
    @staticmethod
    def get_ncf_recommendations(user, limit=20, exclude_rated=True):
        """Get recommendations from your Maximum Performance NCF model"""
        if not ncf_service.is_model_loaded():
            logger.warning("NCF model not loaded, falling back to existing recommendations")
            return []
        
        # Get candidate movies (exclude already rated if specified)
        if exclude_rated:
            rated_movie_ids = Rating.objects.filter(user=user).values_list('movie_id', flat=True)
            candidate_movies = Movie.objects.exclude(id__in=rated_movie_ids)
        else:
            candidate_movies = Movie.objects.all()
        
        candidate_movie_ids = list(candidate_movies.values_list('id', flat=True)[:1000])  # Limit for performance
        
        if not candidate_movie_ids:
            return []
        
        # Get top recommendations from your NCF model
        recommended_movie_ids = ncf_service.get_top_recommendations(
            user.id, 
            candidate_movie_ids, 
            top_k=limit
        )
        
        # Return Movie objects
        movies = Movie.objects.filter(id__in=recommended_movie_ids)
        
        # Maintain order from NCF predictions
        movie_dict = {movie.id: movie for movie in movies}
        ordered_movies = [movie_dict[movie_id] for movie_id in recommended_movie_ids if movie_id in movie_dict]
        
        return ordered_movies
    
    @staticmethod
    def get_cached_ncf_recommendations(user, limit=20):
        """Get NCF recommendations with caching"""
        cache_key = f"ncf_recommendations_{user.id}_{limit}"
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return cached_results
        
        # Generate fresh recommendations
        recommendations = HybridModelService.get_ncf_recommendations(user, limit)
        
        # Cache for 30 minutes
        cache.set(cache_key, recommendations, 1800)
        
        return recommendations
    
    @staticmethod
    def invalidate_user_cache(user):
        """Invalidate NCF cache for user after interactions"""
        cache_patterns = [
            f"ncf_recommendations_{user.id}_*",
            f"hybrid_recommendations_{user.id}_*"
        ]
        
        # Note: This is a simplified version. In production, use pattern-based cache invalidation
        for limit in [10, 20, 50]:  # Common limits
            cache.delete(f"ncf_recommendations_{user.id}_{limit}")
            cache.delete(f"hybrid_recommendations_{user.id}_{limit}")
