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

// Initialize quick action buttons
function initializeQuickActions() {
    // Watchlist button handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.watchlist-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const button = e.target.closest('.watchlist-btn');
            const movieId = button.dataset.movieId;
            const action = button.dataset.action;
            
            if (action === 'add') {
                addToWatchlist(movieId, button);
            } else {
                removeFromWatchlist(movieId, button);
            }
        }
    });
    
    // Rating button handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.rating-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const button = e.target.closest('.rating-btn');
            const movieId = button.dataset.movieId;
            
            showRatingModal(movieId);
        }
    });
    
    // Share button handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.share-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const button = e.target.closest('.share-btn');
            const movieId = button.dataset.movieId;
            
            shareMovie(movieId);
        }
    });
}

// Enhanced watchlist functions
function addToWatchlist(movieId, button = null) {
    if (!button) {
        button = document.querySelector(`[data-movie-id="${movieId}"].watchlist-btn`);
    }
    
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
            
            // Update button state
            if (button) {
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.classList.add('added');
                button.dataset.action = 'remove';
                button.title = 'Remove from Watchlist';
            }
        } else {
            showToast(data.error || 'Failed to add to watchlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error', 'error');
    });
}

function removeFromWatchlist(movieId, button = null) {
    if (!button) {
        button = document.querySelector(`[data-movie-id="${movieId}"].watchlist-btn`);
    }
    
    fetch('/api/watchlist/remove/', {
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
            showToast('Removed from watchlist!', 'success');
            
            // Update button state
            if (button) {
                button.innerHTML = '<i class="fas fa-bookmark"></i>';
                button.classList.remove('added');
                button.dataset.action = 'add';
                button.title = 'Add to Watchlist';
            }
        } else {
            showToast(data.error || 'Failed to remove from watchlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error', 'error');
    });
}

// Enhanced rating modal
function showRatingModal(movieId) {
    // Create and show rating modal
    const modal = createRatingModal(movieId);
    document.body.appendChild(modal);
    
    // Show modal with animation
    setTimeout(() => {
        modal.classList.add('show');
        modal.style.display = 'block';
    }, 10);
}

// Enhanced share function
function shareMovie(movieId) {
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
        }).catch(() => {
            showToast('Failed to copy link', 'error');
        });
    }
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

// Add debouncing for rating operations
const ratingDebounceMap = new Map();

// Rate movie function with debouncing
function rateMovie(movieId, rating, modal) {
    // Create a unique key for this rating operation
    const debounceKey = `${movieId}_${rating}`;
    
    // Check if there's already a rating operation in progress
    if (ratingDebounceMap.has(debounceKey)) {
        console.log('Rating operation already in progress, ignoring duplicate request');
        return;
    }
    
    // Set debounce flag
    ratingDebounceMap.set(debounceKey, true);
    
    // Clear the flag after 3 seconds
    setTimeout(() => {
        ratingDebounceMap.delete(debounceKey);
    }, 3000);
    
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
    .then(response => {
        if (!response.ok) {
            if (response.status === 429) {
                // Rate limited - retry after delay
                return response.json().then(data => {
                    setTimeout(() => {
                        rateMovie(movieId, rating, modal);
                    }, (data.retry_after || 2) * 1000);
                    throw new Error('Rate limited, retrying...');
                });
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showToast(`Rated ${rating} stars!`, 'success');
            modal.remove();
            
            // Update any rating displays on the page
            updateMovieRating(movieId, rating);
            
            // Update movie card if it exists
            const movieCard = document.querySelector(`[data-movie-id="${movieId}"]`);
            if (movieCard) {
                const ratingBadge = movieCard.querySelector('.rating-badge');
                if (ratingBadge) {
                    ratingBadge.innerHTML = `<i class="fas fa-star"></i> ${rating}.0`;
                }
            }
        } else {
            showToast(data.error || 'Failed to rate movie', 'error');
        }
    })
    .catch(error => {
        console.error('Rating error:', error);
        if (!error.message.includes('Rate limited')) {
            showToast('Network error or server issue', 'error');
        }
    })
    .finally(() => {
        // Clear the debounce flag
        ratingDebounceMap.delete(debounceKey);
    });
}

// Enhanced rating modal with click prevention
function createRatingModal(movieId) {
    const currentRating = checkUserRating(movieId);
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
                    ${currentRating ? `<p class="text-muted mb-2">Current rating: ${currentRating} stars</p>` : ''}
                    <div class="star-rating mb-3" data-movie-id="${movieId}">
                        ${[1,2,3,4,5].map(i => `
                            <span class="star ${currentRating && i <= currentRating ? 'text-warning' : ''}" 
                                  data-rating="${i}" 
                                  style="font-size: 2rem; cursor: pointer; color: #6c757d;">★</span>
                        `).join('')}
                    </div>
                    <p class="text-muted">Click a star to rate</p>
                </div>
            </div>
        </div>
    `;
    
    // Add star rating functionality with click prevention
    let isRatingInProgress = false;
    
    modal.querySelectorAll('.star').forEach(star => {
        star.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (isRatingInProgress) {
                console.log('Rating already in progress, ignoring click');
                return;
            }
            
            const rating = parseInt(this.dataset.rating);
            isRatingInProgress = true;
            
            // Disable all stars during rating
            modal.querySelectorAll('.star').forEach(s => {
                s.style.pointerEvents = 'none';
                s.style.opacity = '0.5';
            });
            
            rateMovie(movieId, rating, modal);
        });
        
        star.addEventListener('mouseenter', function() {
            if (!isRatingInProgress) {
                const rating = parseInt(this.dataset.rating);
                highlightStars(modal, rating);
            }
        });
    });
    
    modal.addEventListener('mouseleave', function() {
        if (!isRatingInProgress) {
            highlightStars(modal, currentRating || 0);
        }
    });
    
    return modal;
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

// Enhanced watchlist toggle function
window.toggleWatchlist = function(movieId, isInWatchlist) {
    const endpoint = isInWatchlist ? '/api/watchlist/remove/' : '/api/watchlist/add/';
    const action = isInWatchlist ? 'removeFromWatchlist' : 'addToWatchlist';
    
    fetch(endpoint, {
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
            const message = isInWatchlist ? 'Removed from watchlist!' : 'Added to watchlist!';
            showToast(message, 'success');
            
            // Update UI
            const button = event.target.closest('button');
            if (isInWatchlist) {
                button.innerHTML = '<i class="fas fa-bookmark"></i>';
                button.classList.remove('btn-success');
                button.onclick = () => toggleWatchlist(movieId, false);
            } else {
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.classList.add('btn-success');
                button.onclick = () => toggleWatchlist(movieId, true);
            }
        } else {
            showToast(data.error || 'Failed to update watchlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error', 'error');
    });
};

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