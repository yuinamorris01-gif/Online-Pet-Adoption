/**
 * Modern Hero Slider - ADOPT ME Style
 * Features:
 * - Smooth transitions
 * - Touch/swipe support
 * - Responsive design
 * - Auto-play with pause on hover
 */

class ModernHeroSlider {
  constructor(options = {}) {
    this.container = document.getElementById("heroSlider");
    this.slides = document.querySelectorAll(".hero-slide");
    this.dots = document.querySelectorAll(".slider-dot");
    this.prevBtn = document.getElementById("prevSlide");
    this.nextBtn = document.getElementById("nextSlide");

    // Pet data from Flask template
    this.pets = options.pets || [];
    this.currentIndex = 0;
    this.isTransitioning = false;

    // Auto-play settings
    this.autoPlay = options.autoPlay !== false;
    this.autoPlayDelay = options.autoPlayDelay || 5000;
    this.autoPlayTimer = null;

    // Initialize slider
    this.init();
  }

  init() {
    if (!this.container || this.slides.length === 0) return;

    // Set up event listeners
    this.setupEventListeners();

    // Start auto-play
    if (this.autoPlay) {
      this.startAutoPlay();
    }

    // Initialize first slide
    this.updateSlide(0, false);

    // Initialize GSAP animations
    this.initializeAnimations();
  }

  setupEventListeners() {
    // Navigation arrows
    if (this.prevBtn) {
      this.prevBtn.addEventListener("click", () => this.prevSlide());
    }

    if (this.nextBtn) {
      this.nextBtn.addEventListener("click", () => this.nextSlide());
    }

    // Dot navigation
    this.dots.forEach((dot, index) => {
      dot.addEventListener("click", () => this.goToSlide(index));
    });

    // Keyboard navigation
    document.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") this.prevSlide();
      if (e.key === "ArrowRight") this.nextSlide();
    });

    // Pause auto-play on hover
    if (this.container) {
      this.container.addEventListener("mouseenter", () => this.pauseAutoPlay());
      this.container.addEventListener("mouseleave", () => this.startAutoPlay());
    }

    // Touch/swipe support
    this.setupTouchEvents();
  }

  setupTouchEvents() {
    let startX = 0;
    let startY = 0;
    let endX = 0;
    let endY = 0;

    this.container.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });

    this.container.addEventListener("touchend", (e) => {
      endX = e.changedTouches[0].clientX;
      endY = e.changedTouches[0].clientY;

      const diffX = startX - endX;
      const diffY = startY - endY;

      // Horizontal swipe
      if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
        if (diffX > 0) {
          this.nextSlide();
        } else {
          this.prevSlide();
        }
      }
    });
  }

  nextSlide() {
    if (this.isTransitioning) return;

    const nextIndex = (this.currentIndex + 1) % this.slides.length;
    this.goToSlide(nextIndex);
  }

  prevSlide() {
    if (this.isTransitioning) return;

    const prevIndex =
      this.currentIndex === 0 ? this.slides.length - 1 : this.currentIndex - 1;
    this.goToSlide(prevIndex);
  }

  goToSlide(index) {
    if (this.isTransitioning || index === this.currentIndex) return;

    this.updateSlide(index);
  }

  updateSlide(index, animate = true) {
    if (this.isTransitioning && animate) return;

    this.isTransitioning = true;

    // Remove active class from current slide
    this.slides[this.currentIndex]?.classList.remove("active");
    this.dots[this.currentIndex]?.classList.remove("active");

    // Add active class to new slide
    this.slides[index]?.classList.add("active");
    this.dots[index]?.classList.add("active");

    // Update content if pets data is available
    if (this.pets && this.pets.length > index) {
      this.updateContent(index);
    }

    // Animate content if enabled
    if (animate) {
      this.animateSlideTransition(index);
    }

    this.currentIndex = index;

    // Reset transition flag after animation
    setTimeout(
      () => {
        this.isTransitioning = false;
      },
      animate ? 800 : 0
    );
  }

  updateContent(index) {
    const pet = this.pets[index];
    if (!pet) return;

    // Update hero title
    const heroTitle = document.getElementById("heroTitle");
    if (heroTitle) {
      heroTitle.textContent = pet.name.toUpperCase();
    }

    // Update CTA link - handle both possible IDs
    const heroCTA1 = document.getElementById("heroCTA1");
    const heroCTA2 = document.getElementById("heroCTA2");
    if (heroCTA1) {
      heroCTA1.href = `/adopt/${pet.id}`;
    }
    if (heroCTA2) {
      heroCTA2.href = `/adopt/${pet.id}`;
    }

    // Update pet info card
    const petCounter = document.getElementById("petCounter");
    const petAge = document.getElementById("petAge");
    const petBreed = document.getElementById("petBreed");

    if (petCounter) {
      petCounter.textContent = String(index + 1).padStart(2, "0");
    }

    if (petAge) {
      petAge.textContent = `${pet.age} ${pet.age === 1 ? "year" : "years"}`;
    }

    if (petBreed) {
      petBreed.textContent = pet.breed;
    }
  }

  animateSlideTransition(index) {
    const heroTitle = document.getElementById("heroTitle");
    const heroCTA1 = document.getElementById("heroCTA1");
    const heroCTA2 = document.getElementById("heroCTA2");
    const petInfoCard = document.getElementById("petInfoCard");

    // Create GSAP timeline for smooth animations
    const tl = gsap.timeline();

    // Fade out current content
    tl.to([heroTitle, heroCTA1, heroCTA2, petInfoCard], {
      opacity: 0,
      y: 30,
      duration: 0.3,
      ease: "power2.in",
    })

      // Update content in the middle of animation
      .call(() => {
        this.updateContent(index);
      })

      // Fade in new content
      .to([heroTitle, heroCTA1, heroCTA2, petInfoCard], {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power3.out",
        stagger: 0.1,
      });
  }

  initializeAnimations() {
    // Initial animation for hero elements
    const heroTitle = document.getElementById("heroTitle");
    const heroCTA1 = document.getElementById("heroCTA1");
    const heroCTA2 = document.getElementById("heroCTA2");
    const petInfoCard = document.getElementById("petInfoCard");
    const heroTagline = document.querySelector(".hero-tagline");

    // Set initial states
    gsap.set([heroTitle, heroCTA1, heroCTA2, petInfoCard], {
      opacity: 0,
      y: 50,
    });

    gsap.set(heroTagline, {
      opacity: 0,
      x: 100,
    });

    // Animate elements on page load
    const tl = gsap.timeline({ delay: 0.5 });

    tl.to(heroTagline, {
      opacity: 1,
      x: 0,
      duration: 1,
      ease: "power3.out",
    })

      .to(
        heroTitle,
        {
          opacity: 1,
          y: 0,
          duration: 1.2,
          ease: "power3.out",
        },
        "-=0.7"
      )

      .to(
        [heroCTA1, heroCTA2],
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: "power3.out",
        },
        "-=0.5"
      )

      .to(
        petInfoCard,
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: "power3.out",
        },
        "-=0.6"
      );

    // Add hover animations for interactive elements
    this.setupHoverAnimations();
  }

  setupHoverAnimations() {
    // CTA button hover animation
    const heroCTA1 = document.getElementById("heroCTA1");
    const heroCTA2 = document.getElementById("heroCTA2");

    [heroCTA1, heroCTA2].forEach((cta) => {
      if (cta) {
        cta.addEventListener("mouseenter", () => {
          gsap.to(cta, {
            y: -5,
            scale: 1.05,
            duration: 0.3,
            ease: "power2.out",
          });
        });

        cta.addEventListener("mouseleave", () => {
          gsap.to(cta, {
            y: 0,
            scale: 1,
            duration: 0.3,
            ease: "power2.out",
          });
        });
      }
    });

    // Navigation arrows hover
    [this.prevBtn, this.nextBtn].forEach((btn) => {
      if (btn) {
        btn.addEventListener("mouseenter", () => {
          gsap.to(btn, {
            scale: 1.1,
            backgroundColor: "rgba(212, 165, 116, 0.9)",
            duration: 0.3,
            ease: "power2.out",
          });
        });

        btn.addEventListener("mouseleave", () => {
          gsap.to(btn, {
            scale: 1,
            backgroundColor: "rgba(42, 42, 42, 0.8)",
            duration: 0.3,
            ease: "power2.out",
          });
        });
      }
    });

    // Dots hover animation
    this.dots.forEach((dot) => {
      dot.addEventListener("mouseenter", () => {
        gsap.to(dot, {
          scale: 1.3,
          duration: 0.2,
          ease: "power2.out",
        });
      });

      dot.addEventListener("mouseleave", () => {
        gsap.to(dot, {
          scale: dot.classList.contains("active") ? 1.2 : 1,
          duration: 0.2,
          ease: "power2.out",
        });
      });
    });
  }

  startAutoPlay() {
    if (!this.autoPlay || this.slides.length <= 1) return;

    this.pauseAutoPlay(); // Clear any existing timer

    this.autoPlayTimer = setInterval(() => {
      this.nextSlide();
    }, this.autoPlayDelay);
  }

  pauseAutoPlay() {
    if (this.autoPlayTimer) {
      clearInterval(this.autoPlayTimer);
      this.autoPlayTimer = null;
    }
  }

  // Public API methods
  play() {
    this.autoPlay = true;
    this.startAutoPlay();
  }

  pause() {
    this.autoPlay = false;
    this.pauseAutoPlay();
  }

  destroy() {
    this.pauseAutoPlay();
    // Remove event listeners and clean up
    // Implementation for cleanup if needed
  }
}

// Initialize slider when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  // Get pet data from template (if available)
  const petsData = window.petsData || [];

  // Initialize the modern slider
  window.heroSlider = new ModernHeroSlider({
    pets: petsData,
    autoPlay: true,
    autoPlayDelay: 6000,
  });
});

// Export for use in other scripts
if (typeof module !== "undefined" && module.exports) {
  module.exports = ModernHeroSlider;
}
