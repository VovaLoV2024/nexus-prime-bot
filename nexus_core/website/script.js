/**
 * NEXUS PRIME - MULTIVERSE PORTAL
 * JavaScript Animations & Interactivity
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    initPreloader();
    initStarfield();
    initNavigation();
    initScrollAnimations();
    initCopyButtons();
    initCounter();
    initParallax();
    setLastUpdateDate();
});

/**
 * Preloader
 */
function initPreloader() {
    const preloader = document.getElementById('preloader');
    
    // Hide preloader after page load
    window.addEventListener('load', () => {
        setTimeout(() => {
            preloader.classList.add('hidden');
            
            // Remove from DOM after transition
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }, 1500);
    });
}

/**
 * Animated Starfield Background
 */
function initStarfield() {
    const canvas = document.getElementById('starfield');
    const ctx = canvas.getContext('2d');
    
    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    
    const stars = [];
    const numStars = 200;
    
    // Create stars
    for (let i = 0; i < numStars; i++) {
        stars.push({
            x: Math.random() * width,
            y: Math.random() * height,
            size: Math.random() * 2 + 0.5,
            speed: Math.random() * 0.5 + 0.1,
            brightness: Math.random(),
            direction: Math.random() > 0.5 ? 1 : -1
        });
    }
    
    function animate() {
        ctx.clearRect(0, 0, width, width);
        
        // Gradient background
        const gradient = ctx.createLinearGradient(0, 0, 0, height);
        gradient.addColorStop(0, '#1a1a2e');
        gradient.addColorStop(0.5, '#16213e');
        gradient.addColorStop(1, '#2d1b4e');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
        
        // Draw and update stars
        stars.forEach(star => {
            // Update position
            star.y += star.speed * star.direction;
            
            // Reset if out of bounds
            if (star.y > height) star.y = 0;
            if (star.y < 0) star.y = height;
            
            // Twinkle effect
            star.brightness += (Math.random() - 0.5) * 0.1;
            star.brightness = Math.max(0.3, Math.min(1, star.brightness));
            
            // Draw star
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${star.brightness})`;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    // Handle resize
    window.addEventListener('resize', () => {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    });
}

/**
 * Navigation
 */
function initNavigation() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Update active link based on scroll position
        updateActiveNavLink();
    });
    
    // Mobile menu toggle
    navToggle.addEventListener('click', () => {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Close mobile menu on link click
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 150;
        const sectionHeight = section.offsetHeight;
        
        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

/**
 * Scroll Animations (Intersection Observer)
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Animate child elements with delay
                const children = entry.target.querySelectorAll('.fade-in-up');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('visible');
                    }, index * 150);
                });
            }
        });
    }, observerOptions);
    
    // Observe sections
    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });
    
    // Observe individual elements
    document.querySelectorAll('.fade-in-up').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Copy to Clipboard Functionality
 */
function initCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    const toast = document.getElementById('toast');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const textToCopy = button.getAttribute('data-copy');
            
            try {
                await navigator.clipboard.writeText(textToCopy);
                
                // Show toast notification
                showToast(toast);
                
                // Visual feedback on button
                const originalIcon = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.style.background = 'var(--green-primary)';
                
                setTimeout(() => {
                    button.innerHTML = originalIcon;
                    button.style.background = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
}

function showToast(toast) {
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Animated Counter
 */
function initCounter() {
    const counterElement = document.getElementById('worldCounter');
    const targetNumber = 4;
    let currentNumber = 0;
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const duration = 2000; // 2 seconds
                const increment = targetNumber / (duration / 16); // 60fps
                
                const timer = setInterval(() => {
                    currentNumber += increment;
                    
                    if (currentNumber >= targetNumber) {
                        currentNumber = targetNumber;
                        clearInterval(timer);
                    }
                    
                    counterElement.textContent = Math.floor(currentNumber);
                }, 16);
                
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    if (counterElement) {
        counterObserver.observe(counterElement);
    }
}

/**
 * Parallax Effect
 */
function initParallax() {
    const parallaxElements = document.querySelectorAll('.nexus-symbol, .infinity-symbol');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        
        parallaxElements.forEach(el => {
            const speed = 0.3;
            const yPos = -(scrolled * speed);
            el.style.transform = `translateY(${yPos}px)`;
        });
    });
}

/**
 * Set Last Update Date
 */
function setLastUpdateDate() {
    const lastUpdateElement = document.getElementById('lastUpdate');
    
    if (lastUpdateElement) {
        const currentDate = new Date();
        const year = currentDate.getFullYear();
        lastUpdateElement.textContent = `${year}`;
    }
}

/**
 * Additional Interactive Effects
 */

// World cards tilt effect
document.querySelectorAll('.world-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px) scale(1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
    });
});

// Nexus eye tracking effect
const nexusEye = document.querySelector('.eye-center');
if (nexusEye) {
    document.addEventListener('mousemove', (e) => {
        const rect = nexusEye.getBoundingClientRect();
        const eyeX = rect.left + rect.width / 2;
        const eyeY = rect.top + rect.height / 2;
        
        const angleX = (e.clientX - eyeX) / 30;
        const angleY = (e.clientY - eyeY) / 30;
        
        nexusEye.style.transform = `translate(-50%, -50%) translate(${angleX}px, ${angleY}px)`;
    });
}

// Button ripple effect
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s linear';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        ripple.style.width = '100px';
        ripple.style.height = '100px';
        ripple.style.marginLeft = '-50px';
        ripple.style.marginTop = '-50px';
        ripple.style.pointerEvents = 'none';
        
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Add ripple keyframe animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Console message for developers
console.log('%c👁️ NEXUS PRIME - MULTIVERSE PORTAL 👁️', 
    'font-size: 20px; font-weight: bold; color: #FF6B35;');
console.log('%cNexus видит всё...', 
    'font-size: 14px; color: #7B68EE;');
console.log('%cСоздатель: Вова (VovaLoV) | Помощница: Рокси 🐺', 
    'font-size: 12px; color: #2ECC71;');
