// Pet Adoption System - Main JavaScript File (Tailwind CSS Version)

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeMobileMenu();
    initializeAlerts();
    initializeFormValidation();
    initializeImageLazyLoading();
    initializeModals();
    initializeAnimations();
});

// Mobile menu functionality
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const isOpen = !mobileMenu.classList.contains('hidden');
            
            if (isOpen) {
                mobileMenu.classList.add('hidden');
                // Change hamburger to X
                const paths = mobileMenuButton.querySelectorAll('path');
                paths[0].classList.remove('hidden');
                paths[0].classList.add('inline-flex');
                paths[1].classList.add('hidden');
                paths[1].classList.remove('inline-flex');
            } else {
                mobileMenu.classList.remove('hidden');
                // Change X to hamburger
                const paths = mobileMenuButton.querySelectorAll('path');
                paths[0].classList.add('hidden');
                paths[0].classList.remove('inline-flex');
                paths[1].classList.remove('hidden');
                paths[1].classList.add('inline-flex');
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                if (!mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                    const paths = mobileMenuButton.querySelectorAll('path');
                    paths[0].classList.remove('hidden');
                    paths[0].classList.add('inline-flex');
                    paths[1].classList.add('hidden');
                    paths[1].classList.remove('inline-flex');
                }
            }
        });
    }
}

// Auto-dismiss alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('[class*="bg-green-600"], [class*="bg-red-600"]');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    });
}

// Enhanced form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Lazy loading for images
function initializeImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize modals
function initializeModals() {
    // Confirmation modals for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.dataset.confirmDelete || 'Are you sure you want to delete this item?';
            if (confirm(message)) {
                if (this.tagName === 'A') {
                    window.location.href = this.href;
                } else if (this.form) {
                    this.form.submit();
                }
            }
        });
    });
}

// Initialize animations
function initializeAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    const animateElements = document.querySelectorAll('.card, .pet-card');
    animateElements.forEach(el => observer.observe(el));
}

// Search and filter functionality
class PetFilter {
    constructor() {
        this.form = document.getElementById('filterForm');
        this.inputs = this.form?.querySelectorAll('input, select');
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        // Auto-submit on filter change
        this.inputs?.forEach(input => {
            input.addEventListener('change', this.debounce(() => {
                this.submitForm();
            }, 300));
        });
        
        // Clear filters
        const clearButton = document.querySelector('[data-clear-filters]');
        clearButton?.addEventListener('click', (e) => {
            e.preventDefault();
            this.clearFilters();
        });
    }
    
    submitForm() {
        this.showLoading();
        this.form.submit();
    }
    
    clearFilters() {
        this.inputs?.forEach(input => {
            input.value = '';
        });
        this.submitForm();
    }
    
    showLoading() {
        const button = this.form?.querySelector('button[type="submit"]');
        if (button) {
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
            button.disabled = true;
        }
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Image upload preview
class ImagePreview {
    constructor(inputSelector, previewSelector) {
        this.input = document.querySelector(inputSelector);
        this.preview = document.querySelector(previewSelector);
        this.init();
    }
    
    init() {
        if (!this.input || !this.preview) return;
        
        this.input.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });
        
        // Drag and drop support
        this.setupDragAndDrop();
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.showPreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    }
    
    showPreview(src) {
        this.preview.innerHTML = `
            <img src="${src}" alt="Preview" class="img-fluid rounded shadow">
            <button type="button" class="btn btn-sm btn-danger mt-2" onclick="this.parentElement.innerHTML='<p>No image selected</p>'; document.querySelector('input[type=file]').value='';">
                <i class="fas fa-times"></i> Remove
            </button>
        `;
    }
    
    setupDragAndDrop() {
        const dropZone = this.preview.closest('.card-body') || this.preview;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.input.files = files;
                this.handleFileSelect({ target: { files: files } });
            }
        });
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
}

// Statistics counter animation
class CounterAnimation {
    constructor() {
        this.counters = document.querySelectorAll('.counter-value');
        this.init();
    }
    
    init() {
        if (this.counters.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        this.counters.forEach(counter => observer.observe(counter));
    }
    
    animateCounter(element) {
        const target = parseInt(element.textContent);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }
}

// Back to top button
class BackToTop {
    constructor() {
        this.button = this.createButton();
        this.init();
    }
    
    createButton() {
        const button = document.createElement('button');
        button.innerHTML = '<i class="fas fa-arrow-up"></i>';
        button.className = 'btn btn-primary btn-back-to-top';
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: none;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(button);
        return button;
    }
    
    init() {
        this.button.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                this.button.style.display = 'block';
            } else {
                this.button.style.display = 'none';
            }
        });
    }
}

// Theme toggle (if needed)
class ThemeToggle {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }
    
    init() {
        this.applyTheme();
        const toggle = document.querySelector('[data-theme-toggle]');
        toggle?.addEventListener('click', () => this.toggleTheme());
    }
    
    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('theme', this.theme);
    }
    
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
    }
}

// Initialize components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new PetFilter();
    new ImagePreview('input[type="file"][accept^="image"]', '.image-preview');
    new CounterAnimation();
    new BackToTop();
    // new ThemeToggle(); // Uncomment if theme toggle is needed
});

// Utility functions
const utils = {
    // Format date
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Show toast notification
    showToast: (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const container = document.querySelector('.toast-container') || document.body;
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    // Smooth scroll to element
    scrollTo: (element) => {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    },
    
    // Loading state for buttons
    setButtonLoading: (button, loading = true) => {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    }
};

// Export utils for use in other scripts
window.PetAdoptionUtils = utils;
