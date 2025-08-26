# Real-time Movie Recommendation System

## Overview

This system implements a comprehensive real-time movie recommendation engine that adapts to user interactions in real-time. The system tracks user behavior (clicks, ratings, watchlist additions, searches) and immediately updates movie recommendations to provide a personalized experience.

## Architecture

### 1. Real-time Preference Tracking (`users/preference_service.py`)

The `RealTimePreferenceService` is the core of the system:

- **Interaction Tracking**: Records every user interaction with weighted importance
- **Preference Updates**: Immediately updates genre preferences based on interactions
- **Smart Caching**: Uses Django cache to optimize performance
- **Time Decay**: Preferences naturally decay over time to adapt to changing tastes

### 2. API Endpoints (`api/views.py`)

New real-time endpoints:

- `POST /api/track/` - Track user interactions
- `GET /api/realtime-recommendations/` - Get updated recommendations
- `GET /api/dynamic-carousels/` - Get personalized genre carousels
- `GET /api/user-insights/` - Get user behavior analytics
- `POST /api/refresh/` - Force refresh recommendations

### 3. Frontend JavaScript (`static/js/realtime-recommendations.js`)

Intelligent client-side system:

- **Automatic Tracking**: Monitors all user interactions
- **Smart Updates**: Updates recommendations with appropriate delays
- **Visual Feedback**: Shows users when recommendations are updated
- **Smooth Animations**: Provides polished UI transitions

## How It Works

### Interaction Weights

Different interactions have different impacts on preferences:

```python
INTERACTION_WEIGHTS = {
    'click': 0.1,           # Light interest
    'view_detail': 0.2,     # Moderate interest
    'watchlist_add': 0.4,   # Strong interest
    'watchlist_remove': -0.2, # Negative feedback
    'rate': variable,       # Based on rating value
    'search': 0.1,          # Discovery interest
    'recommendation_click': 0.3, # Algorithm validation
}
```

### Rating-Based Preferences

Ratings provide the strongest signals:

- **1-2 stars**: -0.3 (negative preference)
- **3 stars**: +0.1 (slight positive)
- **4 stars**: +0.5 (strong positive)
- **5 stars**: +0.7 (very strong positive)

### Real-time Updates

1. **User interacts** with a movie (click, rate, add to watchlist)
2. **System tracks** the interaction and updates preferences
3. **Cache is cleared** to force fresh recommendations
4. **Frontend detects** the need for updates (with smart debouncing)
5. **New recommendations** are fetched and displayed
6. **User sees** updated content with smooth animations

## AI Model Integration

The system is designed to work with your AI models:

### Data Export for Training

```bash
# Export user behavior data for AI training
python manage.py export_training_data --format json --output training_data.json
python manage.py export_training_data --format csv --limit 1000
```

### AI Integration Points

1. **User Insights**: Rich user behavior data for model input
2. **Feature Engineering**: Structured data ready for ML models
3. **Prediction Integration**: Easy integration points in the recommendation flow
4. **Model Serving**: Framework for serving trained models

### Example Integration

```python
# In your views.py
from .ai_model_integration_example import DjangoAIIntegration

def home(request):
    # Get base recommendations
    base_movies = RealTimePreferenceService.get_personalized_recommendations(
        request.user, limit=20
    )
    
    # Enhance with AI
    ai_integration = DjangoAIIntegration()
    ai_enhanced_movies = ai_integration.enhance_recommendations(
        request.user, base_movies
    )
    
    context['personalized_movies'] = ai_enhanced_movies
```

## Performance Features

### Intelligent Caching

- **User-specific caches**: Separate cache per user
- **Selective invalidation**: Only clear relevant caches
- **TTL optimization**: Different timeouts for different data types

### Smart Debouncing

- **High-impact actions**: Update immediately (ratings, watchlist)
- **Low-impact actions**: Debounced updates (clicks, views)
- **Batch processing**: Group multiple interactions

### Database Optimization

- **Efficient queries**: Using `select_related` and `prefetch_related`
- **Indexed fields**: Optimized database indexes for fast lookups
- **Query optimization**: Minimal database hits

## User Experience Features

### Visual Feedback

- **Update notifications**: Users see when recommendations change
- **Smooth animations**: Fade-in effects for new content
- **Loading states**: Clear feedback during updates
- **Refresh button**: Manual refresh option

### Adaptive Behavior

- **New user handling**: Graceful fallbacks for users without history
- **Diverse recommendations**: Prevents filter bubbles
- **Trending fallbacks**: Popular content when personalization isn't available

## Configuration

### Settings

Add to your `settings.py`:

```python
# Cache configuration for recommendations
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Recommendation system settings
RECOMMENDATION_CACHE_TIMEOUT = 300  # 5 minutes
GENRE_CAROUSEL_CACHE_TIMEOUT = 600  # 10 minutes
```

### Environment Variables

```bash
# Optional: Enable detailed logging
DJANGO_LOG_LEVEL=INFO

# Optional: AI model settings
AI_MODEL_PATH=/path/to/your/model.joblib
ENABLE_AI_ENHANCEMENT=true
```

## Monitoring and Analytics

### User Insights Dashboard

Access user behavior data:

```javascript
// In browser console
realtimeRecommendations.getUserInsights().then(insights => {
    console.log('User preferences:', insights.genre_preferences);
    console.log('Engagement score:', insights.engagement_score);
});
```

### API Monitoring

Monitor API performance:

- Track response times for recommendation endpoints
- Monitor cache hit rates
- Watch for failed interactions

## Customization

### Adding New Interaction Types

1. **Update the model**:
```python
# In UserInteraction model
interaction_choices = [
    ('click', 'Clicked Movie'),
    ('view_detail', 'Viewed Detail Page'),
    ('rate', 'Rated Movie'),
    ('watchlist_add', 'Added to Watchlist'),
    ('your_new_type', 'Your New Interaction'),  # Add here
]
```

2. **Update the service**:
```python
# In RealTimePreferenceService
INTERACTION_WEIGHTS = {
    'click': 0.1,
    'your_new_type': 0.3,  # Add weight
}
```

3. **Update the frontend**:
```javascript
// In realtime-recommendations.js
document.addEventListener('your-event', (e) => {
    this.trackInteraction(element, 'your_new_type');
});
```

### Custom Recommendation Algorithms

Extend the `RealTimePreferenceService`:

```python
class CustomRecommendationService(RealTimePreferenceService):
    @staticmethod
    def get_custom_recommendations(user, algorithm='collaborative'):
        # Your custom algorithm here
        pass
```

## Troubleshooting

### Common Issues

1. **Recommendations not updating**:
   - Check cache configuration
   - Verify JavaScript is loading
   - Check browser console for errors

2. **Performance issues**:
   - Enable Redis caching
   - Check database query performance
   - Monitor API response times

3. **AI integration issues**:
   - Verify model file paths
   - Check training data format
   - Validate feature engineering

### Debug Mode

Enable debug logging:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'users.preference_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Future Enhancements

### Planned Features

1. **WebSocket Integration**: Real-time updates without polling
2. **A/B Testing Framework**: Test different recommendation algorithms
3. **Multi-armed Bandit**: Optimize recommendation strategies
4. **Social Recommendations**: Friend-based recommendations
5. **Seasonal Adjustments**: Holiday and seasonal content boosting

### AI Model Improvements

1. **Deep Learning Models**: TensorFlow/PyTorch integration
2. **Collaborative Filtering**: User-user and item-item similarity
3. **Content-Based Filtering**: Movie metadata analysis
4. **Hybrid Models**: Combine multiple approaches
5. **Real-time Model Updates**: Online learning capabilities

## API Reference

### Track Interaction

```http
POST /api/track/
Content-Type: application/json

{
    "movie_id": 123,
    "interaction_type": "rate",
    "rating_value": 5,
    "context": {
        "page": "detail",
        "source": "recommendation"
    }
}
```

### Get Real-time Recommendations

```http
GET /api/realtime-recommendations/?limit=10&use_cache=false

Response:
{
    "success": true,
    "recommendations": [...],
    "count": 10
}
```

### Get Dynamic Carousels

```http
GET /api/dynamic-carousels/?max_genres=3

Response:
{
    "success": true,
    "carousels": [
        {
            "title": "More Action Movies for You",
            "subtitle": "Based on your preferences (Score: 0.8)",
            "movies": [...]
        }
    ]
}
```

This real-time recommendation system provides a solid foundation for building sophisticated, AI-powered movie recommendations that adapt to user behavior in real-time.
