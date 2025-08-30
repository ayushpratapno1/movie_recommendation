/**
 * Real-time Movie Recommendation System
 * Handles dynamic updates to movie recommendations based on user interactions
 */

class RealtimeRecommendationSystem {
    constructor() {
        this.apiBase = '/api/';
        this.updateQueue = [];
        this.isProcessing = false;
        this.debounceTimer = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupPeriodicUpdates();
        console.log('Real-time recommendation system initialized');
    }

    /**
     * Setup event listeners for user interactions
     */
    setupEventListeners() {
        // Movie card clicks
        document.addEventListener('click', (e) => {
            const movieCard = e.target.closest('.movie-card');
            if (movieCard) {
                this.trackInteraction(movieCard, 'click');
            }
        });

        // Rating interactions - REMOVED to avoid duplicate tracking
        // The rating API now handles tracking internally
        // document.addEventListener('click', (e) => {
        //     if (e.target.classList.contains('star')) {
        //         const movieId = e.target.closest('[data-movie-id]')?.dataset.movieId;
        //         const rating = parseInt(e.target.dataset.rating);
        //         if (movieId && rating) {
        //             this.trackInteraction({dataset: {movieId}}, 'rate', rating);
        //         }
        //     }
        // });

        // Watchlist interactions - REMOVED to avoid duplicate tracking
        // The watchlist API endpoints now handle tracking internally
        // document.addEventListener('click', (e) => {
        //     if (e.target.classList.contains('watchlist-btn')) {
        //         const movieId = e.target.dataset.movieId;
        //         const action = e.target.classList.contains('add') ? 'watchlist_add' : 'watchlist_remove';
        //         if (movieId) {
        //             this.trackInteraction({dataset: {movieId}}, action);
        //         }
        //     }
        // });

        // Search interactions
        const searchForm = document.querySelector('#search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                const query = e.target.querySelector('input[name="q"]').value;
                if (query.trim()) {
                    this.trackSearchInteraction(query);
                }
            });
        }
    }

    /**
     * Track user interaction and update recommendations
     */
    async trackInteraction(element, interactionType, ratingValue = null) {
        const movieId = element.dataset.movieId;
        if (!movieId) return;

        const context = {
            page: this.getCurrentPage(),
            source: element.dataset.source || 'unknown',
            session_id: this.getSessionId(),
            timestamp: new Date().toISOString()
        };

        try {
            const response = await fetch(`${this.apiBase}track/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    movie_id: movieId,
                    interaction_type: interactionType,
                    rating_value: ratingValue,
                    context: context
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`Tracked ${interactionType} for movie ${movieId}`, data);
                
                // Queue recommendation update
                this.queueRecommendationUpdate(interactionType);
            }
        } catch (error) {
            console.error('Error tracking interaction:', error);
        }
    }

    /**
     * Track search interactions
     */
    async trackSearchInteraction(query) {
        // This would be called when search results are clicked
        // Implementation depends on search results structure
        console.log(`Search interaction: ${query}`);
    }

    /**
     * Queue recommendation updates to avoid too frequent API calls
     */
    queueRecommendationUpdate(interactionType) {
        // Clear existing debounce timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // High-impact interactions update immediately
        const immediateUpdateTypes = ['rate', 'watchlist_add', 'watchlist_remove'];
        const delay = immediateUpdateTypes.includes(interactionType) ? 500 : 2000;

        this.debounceTimer = setTimeout(() => {
            this.updateRecommendations();
        }, delay);
    }

    /**
     * Update recommendations in real-time
     */
    async updateRecommendations() {
        if (this.isProcessing) return;
        this.isProcessing = true;

        try {
            // Update personalized recommendations
            await this.updatePersonalizedSection();
            
            // Update genre carousels
            await this.updateGenreCarousels();

            console.log('Recommendations updated successfully');
        } catch (error) {
            console.error('Error updating recommendations:', error);
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Update personalized recommendations section
     */
    async updatePersonalizedSection() {
        const personalizedSection = document.querySelector('.personalized-movies');
        if (!personalizedSection) return;

        try {
            const response = await fetch(`${this.apiBase}realtime-recommendations/?limit=10&use_cache=false`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.success && data.recommendations.length > 0) {
                this.renderMovieCards(personalizedSection, data.recommendations, 'personalized');
                this.showUpdateIndicator('Recommendations updated based on your activity!');
            }
        } catch (error) {
            console.error('Error updating personalized section:', error);
        }
    }

    /**
     * Update genre carousels
     */
    async updateGenreCarousels() {
        try {
            const response = await fetch(`${this.apiBase}dynamic-carousels/?max_genres=3`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.success && data.carousels.length > 0) {
                this.renderGenreCarousels(data.carousels);
                this.showUpdateIndicator('Your genre preferences have been updated!');
            }
        } catch (error) {
            console.error('Error updating genre carousels:', error);
        }
    }

    /**
     * Render movie cards in a container
     */
    renderMovieCards(container, movies, source) {
        const movieCardsHtml = movies.map(movie => `
            <div class="col-md-3 col-sm-4 mb-3">
                <div class="card movie-card bg-dark text-white animate-fade-in" 
                     data-movie-id="${movie.id}" 
                     data-source="${source}"
                     data-movie-url="/movie/${movie.id}/"
                     style="cursor: pointer;">
                    ${movie.poster_url ? 
                        `<img src="${movie.poster_url}" class="card-img-top" alt="${movie.title}" style="height: 300px; object-fit: cover;">` :
                        `<div class="card-img-top bg-secondary d-flex align-items-center justify-content-center" style="height: 300px;">
                            <i class="fas fa-film fa-3x text-muted"></i>
                         </div>`
                    }
                    <div class="card-body">
                        <h6 class="card-title">${movie.title}</h6>
                        <small class="text-muted">${movie.release_year}</small>
                        <div class="mt-1">
                            ${movie.genres.map(genre => 
                                `<span class="badge bg-primary me-1" style="font-size: 0.7em;">${genre}</span>`
                            ).join('')}
                        </div>
                        ${movie.average_rating > 0 ? 
                            `<div class="mt-1">
                                <small class="text-warning">★ ${movie.average_rating}/5</small>
                             </div>` : ''
                        }
                    </div>
                </div>
            </div>
        `).join('');

        const movieRow = container.querySelector('.row') || container;
        movieRow.innerHTML = movieCardsHtml;
    }

    /**
     * Render genre carousels
     */
    renderGenreCarousels(carousels) {
        const genreCarouselContainer = document.querySelector('.genre-carousels');
        if (!genreCarouselContainer) return;

        const carouselsHtml = carousels.map(carousel => `
            <section class="mb-5 animate-slide-in">
                <h2 class="mb-3 text-white">
                    ${carousel.title}
                    <small class="text-muted">${carousel.subtitle}</small>
                </h2>
                <div class="row movie-carousel">
                    ${carousel.movies.map(movie => `
                        <div class="col-md-3 col-sm-4 mb-3">
                            <div class="card movie-card bg-dark text-white" 
                                 data-movie-id="${movie.id}" 
                                 data-source="genre-${carousel.genre}"
                                 data-movie-url="/movie/${movie.id}/"
                                 style="cursor: pointer;">
                                ${movie.poster_url ? 
                                    `<img src="${movie.poster_url}" class="card-img-top" alt="${movie.title}" style="height: 300px; object-fit: cover;">` :
                                    `<div class="card-img-top bg-secondary d-flex align-items-center justify-content-center" style="height: 300px;">
                                        <i class="fas fa-film fa-3x text-muted"></i>
                                     </div>`
                                }
                                <div class="card-body">
                                    <h6 class="card-title">${movie.title}</h6>
                                    <small class="text-muted">${movie.release_year}</small>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </section>
        `).join('');

        genreCarouselContainer.innerHTML = carouselsHtml;
    }

    /**
     * Show update indicator to user
     */
    showUpdateIndicator(message) {
        // Create or update notification
        let indicator = document.querySelector('.recommendation-update-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'recommendation-update-indicator alert alert-info alert-dismissible fade show position-fixed';
            indicator.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
            document.body.appendChild(indicator);
        }

        indicator.innerHTML = `
            <i class="fas fa-magic me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (indicator && indicator.parentNode) {
                indicator.remove();
            }
        }, 5000);
    }

    /**
     * Setup periodic updates for long-term preference drift
     */
    setupPeriodicUpdates() {
        // Update every 5 minutes if user is active
        setInterval(() => {
            if (document.hasFocus() && !this.isProcessing) {
                this.updateRecommendations();
            }
        }, 5 * 60 * 1000);
    }

    /**
     * Get current page context
     */
    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '/home/') return 'home';
        if (path.includes('/movie/')) return 'detail';
        if (path.includes('/search/')) return 'search';
        if (path.includes('/profile/')) return 'profile';
        return 'other';
    }

    /**
     * Get session ID
     */
    getSessionId() {
        let sessionId = sessionStorage.getItem('movie_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('movie_session_id', sessionId);
        }
        return sessionId;
    }

    /**
     * Get CSRF token
     */
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name=csrf-token]')?.content ||
                     this.getCookie('csrftoken');
        return token;
    }

    /**
     * Get cookie value
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Get user insights (for debugging)
     */
    async getUserInsights() {
        try {
            const response = await fetch(`${this.apiBase}user-insights/`);
            if (response.ok) {
                const data = await response.json();
                console.log('User insights:', data.insights);
                return data.insights;
            }
        } catch (error) {
            console.error('Error getting user insights:', error);
        }
        return null;
    }

    /**
     * Force refresh recommendations
     */
    async forceRefresh() {
        try {
            const response = await fetch(`${this.apiBase}refresh/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (response.ok) {
                await this.updateRecommendations();
                this.showUpdateIndicator('Recommendations have been refreshed!');
            }
        } catch (error) {
            console.error('Error forcing refresh:', error);
        }
    }
}

// CSS animations for smooth updates
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .animate-slide-in {
        animation: slideIn 0.6s ease-out;
    }
    
    .movie-card {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .recommendation-update-indicator {
        animation: slideIn 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeRecommendations = new RealtimeRecommendationSystem();
});

// Expose for debugging
window.RealtimeRecommendationSystem = RealtimeRecommendationSystem;
