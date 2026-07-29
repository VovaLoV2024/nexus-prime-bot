/* ========================================
   NEXUS PRIME BOT - JAVASCRIPT
   ======================================== */

// DOM Elements
const navbar = document.querySelector('.navbar');
const burger = document.querySelector('.burger');
const navLinks = document.querySelector('.nav-links');
const navLinksItems = document.querySelectorAll('.nav-links a');
const scrollIndicator = document.querySelector('.scroll-indicator');

// Mobile Menu Toggle
burger.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    burger.classList.toggle('active');
});

// Close mobile menu when clicking on a link
navLinksItems.forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        burger.classList.remove('active');
    });
});

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    // Hide scroll indicator after scrolling
    if (window.scrollY > 100 && scrollIndicator) {
        scrollIndicator.style.opacity = '0';
        scrollIndicator.style.pointerEvents = 'none';
    }
});

// Smooth Scroll for Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
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

// Copy to Clipboard Function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        showNotification('Скопировано в буфер обмена!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Ошибка копирования', 'error');
    });
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        padding: 15px 25px;
        background: ${type === 'success' ? 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)' : type === 'error' ? 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)' : 'linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%)'};
        color: white;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    // Add animation keyframes
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Intersection Observer for Fade-in Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            
            // Add staggered animation delay for cards
            if (entry.target.classList.contains('feature-card') || 
                entry.target.classList.contains('step-card')) {
                const siblings = entry.target.parentElement.children;
                Array.from(siblings).forEach((sibling, index) => {
                    if (sibling.classList.contains('visible')) {
                        sibling.style.transitionDelay = `${index * 0.1}s`;
                    }
                });
            }
        }
    });
}, observerOptions);

// Observe all elements with fade-in class
document.querySelectorAll('.glass-card, .section-header').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
});

// Active Navigation Link on Scroll
const sections = document.querySelectorAll('section[id]');

function highlightNavLink() {
    const scrollY = window.pageYOffset;
    
    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');
        const navLink = document.querySelector(`.nav-links a[href="#${sectionId}"]`);
        
        if (navLink) {
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLink.classList.add('active');
            } else {
                navLink.classList.remove('active');
            }
        }
    });
}

window.addEventListener('scroll', highlightNavLink);

// Parallax Effect for Hero Section
const heroVisual = document.querySelector('.hero-visual');
if (heroVisual) {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroSection = document.querySelector('.hero');
        const heroHeight = heroSection ? heroSection.offsetHeight : 0;
        
        if (scrolled < heroHeight) {
            heroVisual.style.transform = `translateY(${scrolled * 0.3}px)`;
        }
    });
}

// Counter Animation for Stats
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start);
        }
    }, 16);
}

// Trigger counter animation when stats are visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Add counter animation logic here if needed
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-item').forEach(stat => {
    statsObserver.observe(stat);
});

// Typing Effect for Hero Title (Optional Enhancement)
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Button Ripple Effect
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function(e) {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.cssText = `
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            left: ${x}px;
            top: ${y}px;
            width: 100px;
            height: 100px;
            margin-left: -50px;
            margin-top: -50px;
        `;
        
        // Add ripple animation if not exists
        if (!document.querySelector('#ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

// Floating Elements Animation Enhancement
const floatingElements = document.querySelectorAll('.float-element');
floatingElements.forEach((element, index) => {
    element.style.animationDelay = `${index * 0.5}s`;
});

// Add hover effect to feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.zIndex = '10';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.zIndex = '1';
    });
});

// Loading Animation
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
    
    // Add loaded class styles
    const style = document.createElement('style');
    style.textContent = `
        body.loaded * {
            animation-play-state: running !important;
        }
    `;
    document.head.appendChild(style);
});

// Console Easter Egg
console.log('%c🤖 Nexus Prime Bot', 'font-size: 24px; font-weight: bold; color: #FF6B35;');
console.log('%cСоздано с любовью Вовой (VovaLoV) и Рокси 🐺', 'font-size: 14px; color: #4A90E2;');
console.log('%cВерсия: v1.4.4 Beta', 'font-size: 12px; color: #2ECC71;');

// Performance Optimization: Debounce scroll events
function debounce(func, wait) {
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

// Apply debouncing to scroll event
const debouncedScrollHandler = debounce(() => {
    highlightNavLink();
}, 10);

window.removeEventListener('scroll', highlightNavLink);
window.addEventListener('scroll', debouncedScrollHandler);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Nexus Prime Bot website initialized!');
    
    // Add any initialization code here
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.style.opacity = '0';
        heroTitle.style.transform = 'translateY(20px)';
        setTimeout(() => {
            heroTitle.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            heroTitle.style.opacity = '1';
            heroTitle.style.transform = 'translateY(0)';
        }, 300);
    }
});
