# 🎬 Advanced Movie Recommendation System

Overview
This project solves “what should I watch next?” by delivering personalized, real‑time movie recommendations. A sophisticated, real-time movie recommendation engine built with Django that learns from user behavior and adapts recommendations instantly. Features hybrid AI-powered recommendations, Netflix-like UI, and production-ready architecture.

## 🌟 Key Features

### 🧠 Intelligent Recommendation Engine
- **Real-time Learning**: Adapts recommendations after every user interaction
- **Hybrid AI System**: Combines Neural Collaborative Filtering (NCF) with real-time preference learning
- **Multi-Strategy Approach**: Content-based, collaborative filtering, and popularity-based recommendations
- **Smart Fallbacks**: Graceful handling for new users and cold-start scenarios

### 🎯 User Experience
- **Netflix-like Interface**: Modern, responsive UI with movie carousels and cards
- **Personalized Homepage**: Dynamic sections based on user preferences
- **Interactive Features**: Star ratings, watchlist management, movie search
- **Real-time Updates**: Recommendations refresh automatically as users interact

### 🔧 Technical Excellence
- **Production-Ready**: Security headers, CSRF protection, optimized caching
- **Scalable Architecture**: Modular design with separate apps for movies, users, and API
- **AI Integration**: TensorFlow/Keras models with scikit-learn fallbacks
- **Performance Optimized**: Intelligent caching, database optimization, and efficient queries

## 🏗️ Architecture Overview
# 🎬 Advanced Movie Recommendation System

A sophisticated, real-time movie recommendation engine built with Django that learns from user behavior and adapts recommendations instantly. Features hybrid AI-powered recommendations, Netflix-like UI, and production-ready architecture.


## 🏗️ Architecture Overview
movie_recommendation_system/
├── movie_recommendation/ # Main Django project
│ ├── movies/ # Movie catalog and management
│ │ ├── models.py # Movie, Genre, Person models
│ │ ├── views.py # Home, detail, search views
│ │ ├── tmdb_service.py # TMDb API integration
│ │ └── management/commands/ # Data population commands
│ ├── users/ # User management and preferences
│ │ ├── models.py # UserPreference, Rating, Watchlist
│ │ ├── preference_service.py # Real-time recommendation engine
│ │ └── model_service.py # Hybrid AI model integration
│ ├── api/ # REST API endpoints
│ │ └── views.py # Real-time tracking and recommendations
│ ├── ai_models/ # AI model services
│ │ └── ncf_service.py # Neural Collaborative Filtering
│ └── templates/ # Django templates
├── data/ # Movie dataset
└── requirements.txt # Python dependencies


## 🚀 Quick Start

# AI Model Integration
- Place `max_performance_ncf.keras` and encoders inside `../AI Model/`
- Django app loads model via `model_service.py` (MODEL_PATH setting).
- If model is not found, system falls back to content + popularity recommenders.


### Prerequisites
- Python 3.10+
- Git
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd movie_recommendation_system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r movie_recommendation/requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Optional: Enable TMDb API for movie posters
   set TMDB_API_ENABLED=true
   set TMDB_API_KEY=your_tmdb_api_key
   
   # Required: Django settings
   set DJANGO_SECRET_KEY=your_secret_key
   set DEBUG=true
   ```

5. **Initialize the database**
   ```bash
   cd movie_recommendation
   python manage.py migrate
   python manage.py populate_popular_movies
   python manage.py setup_sample_posters
   ```

6. **Start the server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://127.0.0.1:8000
   - Register a new account
   - Start rating movies and building your profile!


## 🎯 How It Works

### Real-Time Recommendation Engine

The system uses a sophisticated multi-layered approach:

1. **Interaction Tracking**: Every user action (click, rate, watchlist) is tracked with weighted importance
2. **Preference Learning**: Genre preferences are updated in real-time with time decay
3. **Hybrid Recommendations**: Combines multiple strategies based on user engagement level
4. **Smart Caching**: Optimized performance with intelligent cache invalidation

### Recommendation Strategies

#### For New Users (< 5 interactions)
- **NCF**: 25% - Limited collaborative data
- **Real-time**: 35% - Basic preference learning
- **Content-based**: 25% - Genre-based recommendations
- **Popularity**: 15% - Safe popular choices

#### For Active Users (5-50 interactions)
- **NCF**: 45% - Strong collaborative patterns
- **Real-time**: 35% - Preference learning
- **Content-based**: 15% - Genre diversity
- **Popularity**: 5% - Trending content

#### For Power Users (50+ interactions)
- **NCF**: 50% - Primary collaborative engine
- **Real-time**: 35% - Real-time insights
- **Content-based**: 10% - Exploration
- **Popularity**: 5% - Serendipity

### AI Model Integration

The system includes a Neural Collaborative Filtering (NCF) model:

- **TensorFlow/Keras**: Trained deep learning model for collaborative filtering
- **Hybrid Approach**: Combines NCF predictions with real-time preferences
- **Fallback System**: Graceful degradation when AI models are unavailable
- **Performance Optimized**: Cached predictions and efficient batch processing

## 📊 Features Deep Dive

### User Management
- **Registration/Login**: Secure user authentication
- **Profile Management**: Editable preferences and viewing statistics
- **Watchlist**: Save movies for later viewing
- **Rating System**: 1-5 star ratings with persistent UI

### Movie Discovery
- **Search**: Full-text search across movie titles
- **Genre Browsing**: Filter movies by genre
- **Similar Movies**: AI-powered recommendations based on current movie
- **Trending**: Popular movies based on recent interactions

### Real-Time Personalization
- **Dynamic Homepage**: Sections adapt to user preferences
- **Genre Carousels**: Personalized genre-based movie collections
- **Interaction Tracking**: Every click, view, and rating influences recommendations
- **Time Decay**: Preferences naturally evolve over time

## 🔌 API Endpoints

### Core Recommendation APIs
```http
GET /api/hybrid-recommendations/     # Hybrid NCF + real-time recommendations
GET /api/realtime-recommendations/   # Real-time personalized recommendations
GET /api/dynamic-carousels/         # Dynamic genre carousels
GET /api/user-insights/             # User behavior analytics
```

### Interaction Tracking APIs
```http
POST /api/track/                     # Track user interactions
POST /api/rate-movie/               # Rate a movie
POST /api/add-to-watchlist/         # Add to watchlist
POST /api/remove-from-watchlist/    # Remove from watchlist
```

### Example API Usage
```javascript
// Track user interaction
fetch('/api/track/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
        movie_id: 123,
        interaction_type: 'click',
        context: { page: 'home', source: 'trending' }
    })
});

// Get personalized recommendations
fetch('/api/hybrid-recommendations/?limit=20')
    .then(response => response.json())
    .then(data => console.log(data.recommendations));
```

## 🎨 User Interface

### Homepage Sections
- **Personalized Recommendations**: "For You" section based on preferences
- **AI Recommendations**: "Recommended by AI" using NCF model
- **Trending Movies**: Popular movies based on recent interactions
- **Top Rated**: Highest-rated movies in the system
- **Genre Carousels**: Dynamic sections for preferred genres
- **Decade Collections**: Movies organized by release decade

### Movie Detail Page
- **Movie Information**: Title, plot, release year, duration
- **Poster Integration**: TMDb API integration with fallbacks
- **User Actions**: Rate, add to watchlist, view similar movies
- **Similar Movies**: AI-powered recommendations based on current movie

## �� Configuration

### Environment Variables
```bash
# Django Configuration
DJANGO_SECRET_KEY=your_secret_key
DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost

# TMDb API (Optional)
TMDB_API_ENABLED=true
TMDB_API_KEY=your_tmdb_api_key

# AI Model Configuration
NCF_MODEL_ENABLED=true
NCF_MODEL_PATH=/path/to/model.keras
```

### Database Configuration
- **Default**: SQLite (development)
- **Production**: PostgreSQL/MySQL recommended
- **Caching**: Redis recommended for production

## 📈 Performance Features

### Intelligent Caching
- **User-specific caches**: Separate cache per user
- **Selective invalidation**: Only clear relevant caches
- **TTL optimization**: Different timeouts for different data types

### Database Optimization
- **Efficient queries**: Using `select_related` and `prefetch_related`
- **Indexed fields**: Optimized database indexes for fast lookups
- **Query optimization**: Minimal database hits

### Real-Time Updates
- **Smart debouncing**: Prevents excessive API calls
- **Batch processing**: Groups multiple interactions
- **Background processing**: Non-blocking recommendation updates

## 🛠️ Management Commands

### Data Population
```bash
# Populate movies from dataset
python manage.py populate_popular_movies

# Set up sample posters (if TMDb disabled)
python manage.py setup_sample_posters

# Smart movie discovery
python manage.py smart_movie_discovery
```

### AI Model Management
```bash
# Load NCF model
python manage.py load_ncf_model

# Refresh NCF cache
python manage.py refresh_ncf_cache

# Export training data
python manage.py export_training_data --format json
```

## 🔒 Security Features

### Production Security
- **CSRF Protection**: All API endpoints protected
- **Secure Cookies**: HTTPOnly, Secure flags in production
- **HSTS Headers**: HTTP Strict Transport Security
- **Content Security**: XSS protection and content type sniffing prevention

### API Security
- **Authentication Required**: All recommendation endpoints require login
- **Rate Limiting**: Prevents abuse of rating and interaction endpoints
- **Input Validation**: Comprehensive validation of all user inputs

## 🚀 Deployment

### Production Deployment
```bash
# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Start with production server
gunicorn movie_recsys.wsgi:application
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY movie_recommendation/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "movie_recsys.wsgi:application"]
```

## 📊 Monitoring and Analytics

### User Insights
- **Engagement Metrics**: Track user interaction patterns
- **Preference Evolution**: Monitor how user tastes change over time
- **Recommendation Performance**: Measure recommendation accuracy

### System Monitoring
- **API Performance**: Track response times and error rates
- **Cache Hit Rates**: Monitor caching effectiveness
- **Database Performance**: Query optimization and performance metrics

## 🔮 Future Enhancements

### Planned Features
- **WebSocket Integration**: Real-time updates without polling
- **A/B Testing Framework**: Test different recommendation algorithms
- **Social Features**: Friend-based recommendations
- **Multi-language Support**: Internationalization
- **Mobile App**: React Native or Flutter mobile application

### AI Improvements
- **Deep Learning Models**: Advanced neural network architectures
- **Real-time Model Updates**: Online learning capabilities
- **Multi-modal Recommendations**: Text, image, and audio analysis
- **Explainable AI**: Provide reasoning for recommendations

## 🐛 Troubleshooting

### Common Issues

1. **Recommendations not updating**
   - Check cache configuration
   - Verify JavaScript is loading
   - Check browser console for errors

2. **Performance issues**
   - Enable Redis caching
   - Check database query performance
   - Monitor API response times

3. **AI integration issues**
   - Verify model file paths
   - Check training data format
   - Validate feature engineering

### Debug Mode
```python
# Enable debug logging
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

## 📚 Documentation

- **Real-time System**: See `REALTIME_RECOMMENDATIONS.md`
- **TMDb Setup**: See `TMDB_API_SETUP.md`
- **AI Integration**: See `ai_model_integration_example.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## �� Acknowledgments

- **TMDb**: For providing movie data and poster images
- **Django Community**: For the excellent web framework
- **TensorFlow Team**: For the machine learning capabilities
- **Bootstrap**: For the responsive UI components

---

**Built with ❤️ for movie lovers everywhere!** 🍿

For questions or support, please open an issue on GitHub.