import os
import numpy as np
import tensorflow as tf
import joblib
from django.conf import settings
from django.core.cache import cache
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class NCFModelService:
    """
    Neural Collaborative Filtering Model Service
    Loads your trained max_performance_ncf.keras model
    """
    
    _instance = None
    _model = None
    _user_encoder = None
    _movie_encoder = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NCFModelService, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the trained NCF model and encoders"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ai_models', 'models', 'max_performance_ncf.keras')
            user_encoder_path = os.path.join(settings.BASE_DIR, 'ai_models', 'models', 'user_encoder.pkl')
            movie_encoder_path = os.path.join(settings.BASE_DIR, 'ai_models', 'models', 'movie_encoder.pkl')
            
            # Load your trained Maximum Performance NCF model
            self._model = tf.keras.models.load_model(model_path)
            self._user_encoder = joblib.load(user_encoder_path)
            self._movie_encoder = joblib.load(movie_encoder_path)
            
            logger.info("Maximum Performance NCF model loaded successfully")
            logger.info(f"Model parameters: {self._model.count_params():,}")
            
        except Exception as e:
            logger.error(f"Error loading NCF model: {e}")
            self._model = None
    
    def is_model_loaded(self):
        """Check if model is loaded successfully"""
        return self._model is not None
    
    def encode_user_id(self, user_id):
        """Encode Django user ID to model format"""
        try:
            return self._user_encoder.transform([user_id])[0]
        except (ValueError, AttributeError):
            return None
    
    def encode_movie_id(self, movie_id):
        """Encode Django movie ID to model format"""
        try:
            return self._movie_encoder.transform([movie_id])[0]
        except (ValueError, AttributeError):
            return None
    
    def predict_single(self, user_id, movie_id):
        """Predict rating for single user-movie pair"""
        if not self.is_model_loaded():
            return None
        
        user_encoded = self.encode_user_id(user_id)
        movie_encoded = self.encode_movie_id(movie_id)
        
        if user_encoded is None or movie_encoded is None:
            return None
        
        try:
            # Use your trained model for prediction
            prediction = self._model.predict([
                np.array([user_encoded]), 
                np.array([movie_encoded])
            ], verbose=0)[0][0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def predict_batch(self, user_id, movie_ids):
        """Predict ratings for multiple movies for one user"""
        if not self.is_model_loaded():
            return {}
        
        user_encoded = self.encode_user_id(user_id)
        if user_encoded is None:
            return {}
        
        valid_movies = []
        valid_movie_ids = []
        
        for movie_id in movie_ids:
            movie_encoded = self.encode_movie_id(movie_id)
            if movie_encoded is not None:
                valid_movies.append(movie_encoded)
                valid_movie_ids.append(movie_id)
        
        if not valid_movies:
            return {}
        
        try:
            # Batch prediction using your trained model
            user_array = np.array([user_encoded] * len(valid_movies))
            movie_array = np.array(valid_movies)
            
            predictions = self._model.predict([user_array, movie_array], verbose=0)
            
            # Return dictionary mapping movie_id to prediction
            results = {}
            for movie_id, prediction in zip(valid_movie_ids, predictions):
                results[movie_id] = float(prediction[0])
            
            return results
            
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return {}
    
    def get_top_recommendations(self, user_id, candidate_movie_ids, top_k=20):
        """Get top-k movie recommendations for user"""
        predictions = self.predict_batch(user_id, candidate_movie_ids)
        
        if not predictions:
            return []
        
        # Sort by prediction score (descending)
        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        
        return [movie_id for movie_id, score in sorted_predictions[:top_k]]
    
    def get_similar_movies(self, movie_id, top_k=10):
        """Get similar movies using learned embeddings (advanced feature)"""
        # This would require extracting embeddings from your model
        # For now, return empty list - can be implemented later
        return []

# Global instance
ncf_service = NCFModelService()
