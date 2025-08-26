// Enhanced Home Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize enhanced features
    initializeScrollAnimations();
    initializeMovieCardHovers();
    initializeQuickActions();
    initializeLazyLoading();
    
    console.log('🎬 Enhanced Home Page Loaded');
});

// Scroll-based animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.fade-in-up').forEach(el => {
        observer.observe(el);
    });
}

// Enhanced movie card interactions
function initializeMovieCardHovers() {
    document.querySelectorAll('.movie-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Add subtle glow effect
            this.style.boxShadow = '0 20px 40px rgba(0, 123, 255, 0.2)';
            
            // Track hover for analytics (optional)
            const movieId = this.dataset.movieId;
            const source = this.dataset.source;
            
            // Debounced tracking to avoid spam
            clearTimeout(this.hoverTimeout);
            this.hoverTimeout = setTimeout(() => {
                trackInteraction(movieId, 'hover', source);
            }, 500);
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
            clearTimeout(this.hoverTimeout);
        });
        
        // Enhanced click handling
        card.addEventListener('click', function(e) {
            // Don't navigate if clicking on quick action buttons
            if (e.target.closest('.quick-actions')) {
                return;
            }
            
            const movieId = this.dataset.movieId;
            const source = this.dataset.source;
            const url = this.dataset.movieUrl;
            
            // Visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            // Track and navigate
            trackAndNavigate(movieId, source, url);
        });
    });
}

// Quick action buttons
function initializeQuickActions() {
    // These functions are called from the movie card template
    window.addToWatchlist = function(movieId) {
        fetch('/api/watchlist/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({movie_id: movieId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Added to watchlist!', 'success');
                // Update UI
                const button = event.target.closest('button');
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.classList.add('btn-success');
                button.disabled = true;
            } else {
                showToast(data.error || 'Failed to add to watchlist', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error', 'error');
        });
    };
    
    window.showRatingModal = function(movieId) {
        // Create and show rating modal
        const modal = createRatingModal(movieId);
        document.body.appendChild(modal);
        
        // Show modal with animation
        setTimeout(() => {
            modal.classList.add('show');
            modal.style.display = 'block';
        }, 10);
    };
    
    window.shareMovie = function(movieId) {
        const url = `${window.location.origin}/movies/${movieId}/`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Check out this movie!',
                url: url
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(url).then(() => {
                showToast('Movie link copied to clipboard!', 'info');
            });
        }
    };
}

// Lazy loading for images
function initializeLazyLoading() {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Enhanced tracking function
function trackInteraction(movieId, interactionType, source, additionalData = {}) {
    fetch('/api/track/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            movie_id: movieId,
            interaction_type: interactionType,
            context: {
                page: 'home',
                source: source,
                timestamp: new Date().toISOString(),
                ...additionalData
            }
        })
    }).catch(error => {
        console.debug('Tracking error:', error);
    });
}

// Enhanced navigation with better tracking
function trackAndNavigate(movieId, source, url) {
    // Visual feedback
    showToast('Loading movie details...', 'info', 1000);
    
    // Track interaction
    trackInteraction(movieId, 'click', source);
    
    // Navigate with slight delay for tracking
    setTimeout(() => {
        window.location.href = url;
    }, 100);
}

// Create rating modal
function createRatingModal(movieId) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-sm">
            <div class="modal-content bg-dark text-white">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title">Rate this movie</h5>
                    <button type="button" class="btn-close btn-close-white" onclick="this.closest('.modal').remove()"></button>
                </div>
                <div class="modal-body text-center">
                    <div class="star-rating mb-3" data-movie-id="${movieId}">
                        ${[1,2,3,4,5].map(i => `
                            <span class="star" data-rating="${i}" style="font-size: 2rem; cursor: pointer; color: #6c757d;">★</span>
                        `).join('')}
                    </div>
                    <p class="text-muted">Click a star to rate</p>
                </div>
            </div>
        </div>
    `;
    
    // Add star rating functionality
    modal.querySelectorAll('.star').forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            rateMovie(movieId, rating, modal);
        });
        
        star.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            highlightStars(modal, rating);
        });
    });
    
    modal.addEventListener('mouseleave', function() {
        highlightStars(modal, 0);
    });
    
    return modal;
}

// Rate movie function
function rateMovie(movieId, rating, modal) {
    fetch('/api/rate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            movie_id: movieId,
            rating: rating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`Rated ${rating} stars!`, 'success');
            modal.remove();
            // Update any rating displays on the page
            updateMovieRating(movieId, rating);
        } else {
            showToast(data.error || 'Failed to rate movie', 'error');
        }
    })
    .catch(error => {
        console.error('Rating error:', error);
        showToast('Network error', 'error');
    });
}

// Highlight stars in modal
function highlightStars(modal, rating) {
    modal.querySelectorAll('.star').forEach((star, index) => {
        star.style.color = index < rating ? '#ffd700' : '#6c757d';
    });
}

// Update movie rating in UI
function updateMovieRating(movieId, rating) {
    document.querySelectorAll(`[data-movie-id="${movieId}"] .rating-badge`).forEach(badge => {
        badge.innerHTML = `<i class="fas fa-star"></i> ${rating}.0`;
    });
}

// Enhanced toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// Refresh recommendations
function refreshRecommendations() {
    showToast('Refreshing recommendations...', 'info');
    
    fetch('/api/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Recommendations updated!', 'success');
            // Reload the page to show new recommendations
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    })
    .catch(error => {
        showToast('Failed to refresh recommendations', 'error');
    });
}

// Utility function to get CSRF token
function getCookie(name) {
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
