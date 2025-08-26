"""
Example AI Model Integration for Real-time Movie Recommendations

This file demonstrates how you can integrate your AI model with the real-time
recommendation system. The system is designed to be AI-model agnostic.
"""

import json

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"ML libraries not available: {e}")
    print("Install with: pip install scikit-learn pandas numpy joblib")
    SKLEARN_AVAILABLE = False

class MovieRecommendationAI:
    """
    Example AI model integration for movie recommendations
    This is a simplified example - replace with your actual AI model
    """
    
    def __init__(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn and related libraries are required for AI integration")
        self.model = None
        self.scaler = StandardScaler()
        self.genre_encoder = {}
        self.is_trained = False
    
    def prepare_features(self, user_data):
        """
        Convert user preference data into features for the AI model
        
        Args:
            user_data: Dictionary from RealTimePreferenceService.get_user_insights()
        
        Returns:
            numpy array of features
        """
        features = []
        
        # Basic user features
        features.append(user_data.get('average_rating', 0))
        features.append(user_data.get('total_ratings', 0))
        features.append(user_data.get('preference_diversity', 0))
        features.append(user_data.get('engagement_score', 0))
        
        # Genre preferences (top 10 most common genres)
        common_genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 
                        'Sci-Fi', 'Thriller', 'Adventure', 'Crime', 'Fantasy']
        
        genre_prefs = user_data.get('genre_preferences', {})
        for genre in common_genres:
            features.append(genre_prefs.get(genre, 0))
        
        # Interaction patterns
        interactions = user_data.get('recent_interactions', {})
        features.append(interactions.get('click', 0))
        features.append(interactions.get('rate', 0))
        features.append(interactions.get('watchlist_add', 0))
        features.append(interactions.get('view_detail', 0))
        
        return np.array(features).reshape(1, -1)
    
    def train_model(self, training_data_file):
        """
        Train the AI model using exported data
        
        Args:
            training_data_file: Path to JSON file from export_training_data command
        """
        print("Loading training data...")
        with open(training_data_file, 'r') as f:
            data = json.load(f)
        
        # Prepare features and targets
        X = []
        y = []  # For this example, we'll predict engagement score
        
        for user_data in data['data']:
            if user_data.get('engagement_score', 0) > 0:
                features = self.prepare_features(user_data).flatten()
                X.append(features)
                y.append(user_data['engagement_score'])
        
        if len(X) < 10:
            print("Not enough training data. Need at least 10 users with interactions.")
            return False
        
        X = np.array(X)
        y = np.array(y)
        
        # Split and scale data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model (using Random Forest as example)
        print("Training model...")
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training Score: {train_score:.3f}")
        print(f"Test Score: {test_score:.3f}")
        
        self.is_trained = True
        return True
    
    def predict_engagement(self, user_data):
        """
        Predict user engagement score for personalization
        
        Args:
            user_data: Dictionary from RealTimePreferenceService.get_user_insights()
        
        Returns:
            Predicted engagement score (float)
        """
        if not self.is_trained:
            print("Model not trained yet!")
            return 0.5  # Default score
        
        features = self.prepare_features(user_data)
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        return max(0, min(1, prediction))  # Clamp between 0 and 1
    
    def get_genre_recommendations(self, user_data, available_genres):
        """
        Get AI-powered genre recommendations
        
        Args:
            user_data: User insights dictionary
            available_genres: List of available genre names
        
        Returns:
            List of (genre, score) tuples sorted by recommendation score
        """
        if not self.is_trained:
            # Fallback to rule-based recommendations
            return self._rule_based_genre_recommendations(user_data, available_genres)
        
        # For this example, we'll use the current preferences with AI adjustment
        current_prefs = user_data.get('genre_preferences', {})
        engagement_score = self.predict_engagement(user_data)
        
        recommendations = []
        for genre in available_genres:
            base_score = current_prefs.get(genre, 0)
            # AI adjustment based on engagement prediction
            ai_adjusted_score = base_score * engagement_score + (1 - engagement_score) * 0.1
            recommendations.append((genre, ai_adjusted_score))
        
        return sorted(recommendations, key=lambda x: x[1], reverse=True)
    
    def _rule_based_genre_recommendations(self, user_data, available_genres):
        """Fallback rule-based recommendations when AI model isn't available"""
        current_prefs = user_data.get('genre_preferences', {})
        avg_rating = user_data.get('average_rating', 3.0)
        
        recommendations = []
        for genre in available_genres:
            base_score = current_prefs.get(genre, 0)
            # Boost based on average rating (users who rate highly get more diverse recommendations)
            diversity_boost = 0.1 if avg_rating > 4.0 else 0.05
            score = base_score + diversity_boost
            recommendations.append((genre, score))
        
        return sorted(recommendations, key=lambda x: x[1], reverse=True)
    
    def save_model(self, filepath):
        """Save trained model to disk"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'genre_encoder': self.genre_encoder
            }
            joblib.dump(model_data, filepath)
            print(f"Model saved to {filepath}")
        else:
            print("No trained model to save!")
    
    def load_model(self, filepath):
        """Load trained model from disk"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.genre_encoder = model_data['genre_encoder']
            self.is_trained = True
            print(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

# Integration with Django
class DjangoAIIntegration:
    """
    Integration layer between Django app and AI model
    """
    
    def __init__(self):
        self.ai_model = MovieRecommendationAI()
        # Try to load pre-trained model
        try:
            self.ai_model.load_model('movie_recommendation_model.joblib')
        except:
            print("No pre-trained model found. Train a model first.")
    
    def enhance_recommendations(self, user, base_recommendations):
        """
        Enhance base recommendations using AI model
        
        Args:
            user: Django User object
            base_recommendations: QuerySet of Movie objects
        
        Returns:
            Reordered list of movies based on AI predictions
        """
        from users.preference_service import RealTimePreferenceService
        
        # Get user insights
        user_insights = RealTimePreferenceService.get_user_insights(user)
        
        # Get AI engagement prediction
        engagement_score = self.ai_model.predict_engagement(user_insights)
        
        # Convert to list and add AI scoring
        movies_with_scores = []
        for movie in base_recommendations:
            # Calculate AI-enhanced score
            genre_scores = []
            for genre in movie.genres.all():
                genre_recs = self.ai_model.get_genre_recommendations(
                    user_insights, [genre.name]
                )
                if genre_recs:
                    genre_scores.append(genre_recs[0][1])
            
            avg_genre_score = sum(genre_scores) / len(genre_scores) if genre_scores else 0.1
            ai_score = avg_genre_score * engagement_score
            
            movies_with_scores.append((movie, ai_score))
        
        # Sort by AI score
        movies_with_scores.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in movies_with_scores]

# Example usage in Django views
def integrate_with_django_view():
    """
    Example of how to integrate this with your Django views
    """
    # This would be in your movies/views.py
    
    # from .ai_model_integration_example import DjangoAIIntegration
    # 
    # def home(request):
    #     # ... existing code ...
    #     
    #     # Get base recommendations
    #     personalized_movies = RealTimePreferenceService.get_personalized_recommendations(
    #         request.user, limit=20
    #     )
    #     
    #     # Enhance with AI
    #     ai_integration = DjangoAIIntegration()
    #     ai_enhanced_movies = ai_integration.enhance_recommendations(
    #         request.user, personalized_movies
    #     )[:10]  # Take top 10
    #     
    #     context['personalized_movies'] = ai_enhanced_movies
    #     
    #     # ... rest of view ...

if __name__ == "__main__":
    # Example training workflow
    print("Movie Recommendation AI Model Example")
    print("=====================================")
    
    # Initialize AI model
    ai = MovieRecommendationAI()
    
    print("\n1. Export training data using Django command:")
    print("   python manage.py export_training_data --format json --output training_data.json")
    
    print("\n2. Train the model:")
    print("   # This would train on your exported data")
    print("   # ai.train_model('training_data.json')")
    
    print("\n3. Save the trained model:")
    print("   # ai.save_model('movie_recommendation_model.joblib')")
    
    print("\n4. Use in Django views:")
    print("   # See integrate_with_django_view() function above")
    
    print("\nThe system is ready for AI integration!")
    print("Replace this example with your actual ML model (TensorFlow, PyTorch, etc.)")
