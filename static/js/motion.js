// Pet Adoption System - Framer Motion-Style Animation Library
// Inspired by Framer Motion API for vanilla JavaScript

class MotionElement {
    constructor(element) {
        this.element = element;
        this.animations = new Map();
        this.listeners = new Map();
        this.variants = {};
        this.currentVariant = 'initial';
        this.isAnimating = false;
        
        // Initialize element for motion
        this.setupElement();
    }
    
    setupElement() {
        // Add motion classes and setup
        this.element.style.willChange = 'transform, opacity';
        this.element.classList.add('motion-element');
    }
    
    // Framer Motion-style animate method
    animate(keyframes, options = {}) {
        const {
            duration = 0.6,
            ease = 'power2.out',
            delay = 0,
            stagger = 0,
            repeat = 0,
            yoyo = false,
            onStart = null,
            onComplete = null,
            onUpdate = null
        } = options;

        // Convert Framer Motion easing to GSAP easing
        const gsapEase = this.convertEasing(ease);
        
        // Create animation timeline
        const tl = gsap.timeline({
            delay,
            onStart: () => {
                this.isAnimating = true;
                if (onStart) onStart();
            },
            onComplete: () => {
                this.isAnimating = false;
                if (onComplete) onComplete();
            },
            onUpdate: onUpdate
        });
        
        // Handle different keyframe formats
        if (Array.isArray(keyframes)) {
            // Array of keyframes
            keyframes.forEach((keyframe, index) => {
                const frameDelay = index * (stagger || 0);
                tl.to(this.element, {
                    ...keyframe,
                    duration: duration / keyframes.length,
                    ease: gsapEase
                }, frameDelay);
            });
        } else {
            // Single keyframe object
            tl.to(this.element, {
                ...keyframes,
                duration,
                ease: gsapEase
            });
        }
        
        // Handle repeat
        if (repeat > 0) {
            tl.repeat(repeat);
            if (yoyo) tl.yoyo(true);
        }
        
        return {
            then: (callback) => {
                tl.eventCallback('onComplete', callback);
                return this;
            },
            stop: () => tl.kill()
        };
    }
    
    // Framer Motion-style variants
    setVariants(variants) {
        this.variants = variants;
        return this;
    }
    
    // Animate to variant
    animateToVariant(variantName, options = {}) {
        if (this.variants[variantName]) {
            this.currentVariant = variantName;
            return this.animate(this.variants[variantName], options);
        }
        return Promise.resolve();
    }
    
    // Framer Motion-style initial state
    initial(state) {
        gsap.set(this.element, state);
        return this;
    }
    
    // Gesture-based animations
    whileHover(animation, options = {}) {
        const hoverIn = () => this.animate(animation, options);
        const hoverOut = () => this.animate(this.getResetState(animation), { duration: 0.3 });
        
        this.element.addEventListener('mouseenter', hoverIn);
        this.element.addEventListener('mouseleave', hoverOut);
        
        this.listeners.set('hover', { hoverIn, hoverOut });
        return this;
    }
    
    whileTap(animation, options = {}) {
        const tapStart = () => this.animate(animation, { duration: 0.1, ...options });
        const tapEnd = () => this.animate(this.getResetState(animation), { duration: 0.2 });
        
        this.element.addEventListener('mousedown', tapStart);
        this.element.addEventListener('mouseup', tapEnd);
        this.element.addEventListener('mouseleave', tapEnd);
        
        // Touch events
        this.element.addEventListener('touchstart', tapStart);
        this.element.addEventListener('touchend', tapEnd);
        
        this.listeners.set('tap', { tapStart, tapEnd });
        return this;
    }
    
    // Drag functionality (simplified)
    drag(options = {}) {
        const { bounds = 'parent', axis = 'both' } = options;
        
        Draggable.create(this.element, {
            bounds: bounds,
            type: axis === 'x' ? 'x' : axis === 'y' ? 'y' : 'x,y',
            inertia: true,
            onDragStart: () => {
                this.element.style.zIndex = '1000';
                gsap.to(this.element, { scale: 1.1, duration: 0.2 });
            },
            onDragEnd: () => {
                gsap.to(this.element, { scale: 1, duration: 0.2, delay: 0.1 });
                this.element.style.zIndex = '';
            }
        });
        
        return this;
    }
    
    // Layout animations (position changes)
    layoutAnimation(options = {}) {
        const { duration = 0.6, ease = 'power2.out' } = options;
        
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
                    this.handleLayoutChange(duration, ease);
                }
            });
        });
        
        observer.observe(this.element, {
            attributes: true,
            attributeFilter: ['style', 'class']
        });
        
        return this;
    }
    
    // Scroll-triggered animations
    scrollTrigger(animation, options = {}) {
        const {
            trigger = this.element,
            start = 'top 80%',
            end = 'bottom 20%',
            once = true,
            ...animOptions
        } = options;
        
        ScrollTrigger.create({
            trigger,
            start,
            end,
            once,
            onEnter: () => this.animate(animation, animOptions),
            onLeave: once ? null : () => this.animate(this.getResetState(animation), animOptions)
        });
        
        return this;
    }
    
    // Parallax effect
    parallax(options = {}) {
        const { speed = 0.5, direction = 'vertical' } = options;
        
        ScrollTrigger.create({
            trigger: this.element,
            start: 'top bottom',
            end: 'bottom top',
            scrub: true,
            onUpdate: (self) => {
                const progress = self.progress;
                const movement = progress * 100 * speed;
                
                if (direction === 'vertical') {
                    gsap.set(this.element, { y: movement });
                } else {
                    gsap.set(this.element, { x: movement });
                }
            }
        });
        
        return this;
    }
    
    // Helper methods
    convertEasing(ease) {
        const easingMap = {
            'linear': 'none',
            'easeIn': 'power2.in',
            'easeOut': 'power2.out',
            'easeInOut': 'power2.inOut',
            'anticipate': 'back.out(1.7)',
            'backIn': 'back.in(1.7)',
            'backOut': 'back.out(1.7)',
            'backInOut': 'back.inOut(1.7)',
            'bounceIn': 'bounce.in',
            'bounceOut': 'bounce.out',
            'bounceInOut': 'bounce.inOut',
            'elasticIn': 'elastic.in(1, 0.3)',
            'elasticOut': 'elastic.out(1, 0.3)',
            'elasticInOut': 'elastic.inOut(1, 0.3)'
        };
        
        return easingMap[ease] || ease;
    }
    
    getResetState(animation) {
        const reset = {};
        Object.keys(animation).forEach(key => {
            switch (key) {
                case 'x':
                case 'y':
                case 'z':
                case 'rotateX':
                case 'rotateY':
                case 'rotateZ':
                case 'rotate':
                    reset[key] = 0;
                    break;
                case 'scale':
                case 'scaleX':
                case 'scaleY':
                case 'opacity':
                    reset[key] = 1;
                    break;
                case 'skewX':
                case 'skewY':
                    reset[key] = 0;
                    break;
            }
        });
        return reset;
    }
    
    handleLayoutChange(duration, ease) {
        // Simplified layout animation
        gsap.to(this.element, {
            duration,
            ease: this.convertEasing(ease)
        });
    }
    
    // Cleanup
    destroy() {
        // Remove all listeners
        this.listeners.forEach((listener, type) => {
            if (type === 'hover') {
                this.element.removeEventListener('mouseenter', listener.hoverIn);
                this.element.removeEventListener('mouseleave', listener.hoverOut);
            } else if (type === 'tap') {
                this.element.removeEventListener('mousedown', listener.tapStart);
                this.element.removeEventListener('mouseup', listener.tapEnd);
                this.element.removeEventListener('touchstart', listener.tapStart);
                this.element.removeEventListener('touchend', listener.tapEnd);
            }
        });
        
        // Kill any running animations
        gsap.killTweensOf(this.element);
        
        // Clear maps
        this.animations.clear();
        this.listeners.clear();
    }
}

// Main Motion class (similar to Framer Motion's motion)
class Motion {
    // Create motion element
    static create(selector) {
        const elements = typeof selector === 'string' 
            ? document.querySelectorAll(selector)
            : [selector];
            
        if (elements.length === 1) {
            return new MotionElement(elements[0]);
        }
        
        // Return array of motion elements for multiple elements
        return Array.from(elements).map(el => new MotionElement(el));
    }
    
    // Stagger animations (like Framer Motion's stagger)
    static stagger(elements, animation, options = {}) {
        const {
            staggerDelay = 0.1,
            from = 'start', // 'start', 'end', 'center', or index
            ease = 'power2.out',
            duration = 0.6,
            ...animOptions
        } = options;
        
        const motionElements = Array.from(elements).map(el => 
            typeof el === 'string' ? document.querySelector(el) : el
        );
        
        // Calculate stagger delays
        const delays = this.calculateStaggerDelays(motionElements.length, staggerDelay, from);
        
        // Animate each element
        const promises = motionElements.map((element, index) => {
            const motionEl = new MotionElement(element);
            return motionEl.animate(animation, {
                delay: delays[index],
                duration,
                ease,
                ...animOptions
            });
        });
        
        return Promise.all(promises);
    }
    
    // Calculate stagger delays based on 'from' option
    static calculateStaggerDelays(length, staggerDelay, from) {
        const delays = [];
        
        switch (from) {
            case 'end':
                for (let i = 0; i < length; i++) {
                    delays[i] = (length - 1 - i) * staggerDelay;
                }
                break;
            case 'center':
                const center = Math.floor(length / 2);
                for (let i = 0; i < length; i++) {
                    delays[i] = Math.abs(i - center) * staggerDelay;
                }
                break;
            case 'start':
            default:
                for (let i = 0; i < length; i++) {
                    delays[i] = i * staggerDelay;
                }
                break;
        }
        
        if (typeof from === 'number') {
            for (let i = 0; i < length; i++) {
                delays[i] = Math.abs(i - from) * staggerDelay;
            }
        }
        
        return delays;
    }
    
    // Global animation controls
    static timeline() {
        return gsap.timeline();
    }
    
    // Smooth scroll implementation
    static smoothScroll(options = {}) {
        const lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            orientation: 'vertical',
            gestureOrientation: 'vertical',
            smoothWheel: true,
            ...options
        });
        
        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        
        requestAnimationFrame(raf);
        
        return lenis;
    }
    
    // Page transition utilities
    static pageTransition(options = {}) {
        const {
            duration = 0.8,
            ease = 'power2.inOut',
            exitAnimation = { opacity: 0, y: -50 },
            enterAnimation = { opacity: 1, y: 0 }
        } = options;
        
        return {
            exit: (element) => {
                const motionEl = new MotionElement(element);
                return motionEl.animate(exitAnimation, { duration: duration / 2, ease });
            },
            enter: (element) => {
                const motionEl = new MotionElement(element);
                motionEl.initial({ opacity: 0, y: 50 });
                return motionEl.animate(enterAnimation, { 
                    duration: duration / 2, 
                    ease,
                    delay: duration / 4
                });
            }
        };
    }
    
    // Intersection Observer with Motion animations
    static observeInView(elements, animation, options = {}) {
        const {
            threshold = 0.1,
            rootMargin = '0px 0px -10% 0px',
            once = true,
            ...animOptions
        } = options;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const motionEl = new MotionElement(entry.target);
                    motionEl.animate(animation, animOptions);
                    
                    if (once) {
                        observer.unobserve(entry.target);
                    }
                }
            });
        }, { threshold, rootMargin });
        
        elements.forEach(el => {
            const element = typeof el === 'string' ? document.querySelector(el) : el;
            if (element) observer.observe(element);
        });
        
        return observer;
    }
}

// Export for use
window.Motion = Motion;
window.MotionElement = MotionElement;

// Common animation presets (Framer Motion style)
Motion.presets = {
    fadeIn: { opacity: 1 },
    fadeOut: { opacity: 0 },
    slideInUp: { y: 0, opacity: 1 },
    slideInDown: { y: 0, opacity: 1 },
    slideInLeft: { x: 0, opacity: 1 },
    slideInRight: { x: 0, opacity: 1 },
    slideOutUp: { y: -50, opacity: 0 },
    slideOutDown: { y: 50, opacity: 0 },
    slideOutLeft: { x: -50, opacity: 0 },
    slideOutRight: { x: 50, opacity: 0 },
    scaleIn: { scale: 1, opacity: 1 },
    scaleOut: { scale: 0.8, opacity: 0 },
    rotateIn: { rotate: 0, opacity: 1 },
    bounceIn: { scale: 1, opacity: 1 },
    flipIn: { rotateY: 0, opacity: 1 },
    
    // Hover effects
    lift: { y: -10, scale: 1.02 },
    grow: { scale: 1.05 },
    shrink: { scale: 0.95 },
    rotate: { rotate: 5 },
    
    // Loading animations
    pulse: { scale: [1, 1.05, 1] },
    heartbeat: { scale: [1, 1.1, 1] },
    wobble: { rotate: [0, -5, 5, -5, 5, 0] }
};

// Initialize motion system
document.addEventListener('DOMContentLoaded', () => {
    // Register GSAP plugins
    gsap.registerPlugin(ScrollTrigger, Draggable);
    
    // Auto-initialize elements with motion attributes
    Motion.autoInit();
});

// Auto-initialization for elements with data-motion attributes
Motion.autoInit = () => {
    // Handle elements with data-motion-hover
    document.querySelectorAll('[data-motion-hover]').forEach(el => {
        const animation = el.dataset.motionHover;
        const preset = Motion.presets[animation];
        if (preset) {
            Motion.create(el).whileHover(preset);
        }
    });
    
    // Handle elements with data-motion-tap
    document.querySelectorAll('[data-motion-tap]').forEach(el => {
        const animation = el.dataset.motionTap;
        const preset = Motion.presets[animation];
        if (preset) {
            Motion.create(el).whileTap(preset);
        }
    });
    
    // Handle elements with data-motion-scroll
    document.querySelectorAll('[data-motion-scroll]').forEach(el => {
        const animation = el.dataset.motionScroll;
        const preset = Motion.presets[animation];
        if (preset) {
            Motion.create(el).scrollTrigger(preset);
        }
    });
};
