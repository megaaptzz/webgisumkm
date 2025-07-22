// Mobile Navigation and WebGIS Optimizations
document.addEventListener('DOMContentLoaded', function() {
    
    // ========== MOBILE NAVIGATION SETUP ==========
    function initMobileNavigation() {
        const nav = document.querySelector('nav');
        if (!nav) return;
        
        // Create mobile navigation toggle button
        const navToggle = document.createElement('button');
        navToggle.className = 'nav-toggle';
        navToggle.innerHTML = '<i class="fas fa-bars"></i> Menu';
        navToggle.setAttribute('aria-label', 'Toggle navigation menu');
        navToggle.setAttribute('aria-expanded', 'false');
        
        // Insert toggle button before nav ul
        const navUl = nav.querySelector('ul');
        if (navUl) {
            nav.insertBefore(navToggle, navUl);
            
            // Add initial ARIA attributes
            navUl.setAttribute('id', 'main-navigation');
            navToggle.setAttribute('aria-controls', 'main-navigation');
            
            // Toggle navigation menu
            navToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                toggleNavigation();
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!nav.contains(e.target) && navUl.classList.contains('active')) {
                    closeNavigation();
                }
            });
            
            // Close menu when pressing Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && navUl.classList.contains('active')) {
                    closeNavigation();
                    navToggle.focus();
                }
            });
            
            // Setup navigation links
            setupNavigationLinks();
        }
        
        function toggleNavigation() {
            const isActive = navUl.classList.contains('active');
            if (isActive) {
                closeNavigation();
            } else {
                openNavigation();
            }
        }
        
        function openNavigation() {
            navUl.classList.add('active');
            navToggle.innerHTML = '<i class="fas fa-times"></i> Close';
            navToggle.setAttribute('aria-expanded', 'true');
            
            // Focus first navigation link for accessibility
            const firstLink = navUl.querySelector('a');
            if (firstLink) {
                setTimeout(() => firstLink.focus(), 100);
            }
        }
        
        function closeNavigation() {
            navUl.classList.remove('active');
            navToggle.innerHTML = '<i class="fas fa-bars"></i> Menu';
            navToggle.setAttribute('aria-expanded', 'false');
        }
        
        function setupNavigationLinks() {
            const navLinks = navUl.querySelectorAll('a');
            
            navLinks.forEach((link, index) => {
                // Close menu when clicking on nav links
                link.addEventListener('click', function(e) {
                    closeNavigation();
                    
                    // Handle smooth scrolling for anchor links
                    const href = this.getAttribute('href');
                    if (href && href.startsWith('#')) {
                        e.preventDefault();
                        smoothScrollToElement(href);
                        updateActiveNavLink(this);
                    }
                });
                
                // Keyboard navigation support
                link.addEventListener('keydown', function(e) {
                    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                        e.preventDefault();
                        const direction = e.key === 'ArrowDown' ? 1 : -1;
                        const nextIndex = (index + direction + navLinks.length) % navLinks.length;
                        navLinks[nextIndex].focus();
                    }
                });
            });
        }
    }
    
    // ========== SMOOTH SCROLLING ==========
    function smoothScrollToElement(targetId) {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            const headerHeight = document.querySelector('header').offsetHeight;
            const targetPosition = targetElement.offsetTop - headerHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }
    
    // ========== ACTIVE NAVIGATION STATE ==========
    function updateActiveNavLink(activeLink) {
        const navLinks = document.querySelectorAll('nav a');
        navLinks.forEach(link => link.classList.remove('active'));
        activeLink.classList.add('active');
    }
    
    // ========== SCROLL-BASED NAVIGATION HIGHLIGHTING ==========
    function initScrollNavigation() {
        const sections = document.querySelectorAll('.section[id]');
        const navLinks = document.querySelectorAll('nav a[href^="#"]');
        
        if (sections.length === 0 || navLinks.length === 0) return;
        
        let scrollTimeout;
        
        window.addEventListener('scroll', function() {
            // Throttle scroll events for performance
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(function() {
                updateNavigationOnScroll();
            }, 50);
        }, { passive: true });
        
        function updateNavigationOnScroll() {
            const scrollPosition = window.pageYOffset;
            const headerHeight = document.querySelector('header').offsetHeight;
            
            let activeSection = null;
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - headerHeight - 100;
                const sectionBottom = sectionTop + section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                    activeSection = section;
                }
            });
            
            // Update active navigation link
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (activeSection && link.getAttribute('href') === '#' + activeSection.id) {
                    link.classList.add('active');
                }
            });
        }
    }
    
    // ========== IFRAME OPTIMIZATION ==========
    function optimizeMapIframe() {
        const mapIframe = document.querySelector('.map-container iframe');
        if (!mapIframe) return;
        
        // Add loading state
        const mapContainer = mapIframe.parentElement;
        const loadingIndicator = createLoadingIndicator();
        mapContainer.appendChild(loadingIndicator);
        
        // Handle iframe load
        mapIframe.addEventListener('load', function() {
            loadingIndicator.remove();
            
            // Add mobile-specific iframe optimizations
            if (window.innerWidth <= 768) {
                optimizeIframeForMobile(mapIframe);
            }
        });
        
        // Handle iframe errors
        mapIframe.addEventListener('error', function() {
            loadingIndicator.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;"><i class="fas fa-exclamation-triangle"></i> Map failed to load</p>';
        });
    }
    
    function createLoadingIndicator() {
        const loading = document.createElement('div');
        loading.className = 'map-loading';
        loading.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        `;
        loading.innerHTML = `
            <div style="text-align: center; color: #003366;">
                <div class="loading-spinner" style="
                    width: 40px;
                    height: 40px;
                    border: 4px solid rgba(0, 51, 102, 0.1);
                    border-radius: 50%;
                    border-top-color: #003366;
                    animation: spin 1s ease-in-out infinite;
                    margin: 0 auto 1rem;
                "></div>
                <p>Loading map...</p>
            </div>
        `;
        return loading;
    }
    
    function optimizeIframeForMobile(iframe) {
        // Send message to iframe for mobile optimization
        try {
            iframe.contentWindow.postMessage({
                type: 'MOBILE_OPTIMIZATION',
                data: {
                    isMobile: true,
                    screenWidth: window.innerWidth,
                    screenHeight: window.innerHeight
                }
            }, '*');
        } catch (e) {
            console.log('Could not communicate with iframe for mobile optimization');
        }
    }
    
    // ========== RESPONSIVE IMAGE LOADING ==========
    function optimizeImages() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            // Add loading="lazy" for performance
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            
            // Add error handling
            img.addEventListener('error', function() {
                this.style.display = 'none';
            });
        });
    }
    
    // ========== TOUCH GESTURE SUPPORT ==========
    function initTouchGestures() {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        
        const minSwipeDistance = 50;
        const maxVerticalDistance = 100;
        
        document.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].clientX;
            touchStartY = e.changedTouches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].clientX;
            touchEndY = e.changedTouches[0].clientY;
            handleSwipeGesture();
        }, { passive: true });
        
        function handleSwipeGesture() {
            const horizontalDistance = touchEndX - touchStartX;
            const verticalDistance = Math.abs(touchEndY - touchStartY);
            
            // Only process horizontal swipes
            if (verticalDistance > maxVerticalDistance) return;
            
            const nav = document.querySelector('nav');
            const navUl = nav?.querySelector('ul');
            
            if (!nav || !navUl) return;
            
            // Swipe right to open menu
            if (horizontalDistance > minSwipeDistance && !navUl.classList.contains('active')) {
                const navToggle = nav.querySelector('.nav-toggle');
                if (navToggle && window.innerWidth <= 768) {
                    navToggle.click();
                }
            }
            
            // Swipe left to close menu
            if (horizontalDistance < -minSwipeDistance && navUl.classList.contains('active')) {
                const navToggle = nav.querySelector('.nav-toggle');
                if (navToggle) {
                    navToggle.click();
                }
            }
        }
    }
    
    // ========== VIEWPORT HEIGHT FIX FOR MOBILE ==========
    function fixMobileViewportHeight() {
        // Fix for mobile browsers that change viewport height on scroll
        function setViewportHeight() {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }
        
        setViewportHeight();
        
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(setViewportHeight, 250);
        });
        
        // Also update on orientation change
        window.addEventListener('orientationchange', function() {
            setTimeout(setViewportHeight, 500);
        });
    }
    
    // ========== PERFORMANCE MONITORING ==========
    function initPerformanceOptimizations() {
        // Lazy load sections that are not immediately visible
        if ('IntersectionObserver' in window) {
            const sectionObserver = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('section-visible');
                        sectionObserver.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px'
            });
            
            document.querySelectorAll('.section').forEach(section => {
                sectionObserver.observe(section);
            });
        }
        
        // Preload critical resources
        const criticalResources = [
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'style';
            link.href = resource;
            document.head.appendChild(link);
        });
    }
    
    // ========== ACCESSIBILITY IMPROVEMENTS ==========
    function improveAccessibility() {
        // Add skip link for keyboard navigation
        const skipLink = document.createElement('a');
        skipLink.href = '#main';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #003366;
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10001;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', function() {
            this.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', function() {
            this.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Add main landmark if it doesn't exist
        const main = document.querySelector('main');
        if (main && !main.id) {
            main.id = 'main';
        }
        
        // Improve heading hierarchy
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach((heading, index) => {
            if (!heading.id) {
                heading.id = `heading-${index + 1}`;
            }
        });
        
        // Add ARIA labels to interactive elements
        const buttons = document.querySelectorAll('button:not([aria-label])');
        buttons.forEach(button => {
            if (!button.getAttribute('aria-label') && button.textContent.trim()) {
                button.setAttribute('aria-label', button.textContent.trim());
            }
        });
    }
    
    // ========== ERROR HANDLING ==========
    function initErrorHandling() {
        // Global error handler
        window.addEventListener('error', function(e) {
            console.error('JavaScript error:', e.error);
            
            // Show user-friendly error message for critical failures
            if (e.filename && e.filename.includes('script.js')) {
                showErrorNotification('Some features may not work properly. Please refresh the page.');
            }
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', function(e) {
            console.error('Unhandled promise rejection:', e.reason);
            e.preventDefault();
        });
    }
    
    function showErrorNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #e74c3c;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            z-index: 10002;
            max-width: 300px;
            font-size: 0.9rem;
        `;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; margin-left: auto;">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    // ========== MOBILE-SPECIFIC OPTIMIZATIONS ==========
    function initMobileOptimizations() {
        if (window.innerWidth <= 768) {
            // Disable hover effects on mobile
            document.body.classList.add('mobile-device');
            
            // Optimize touch targets
            const touchTargets = document.querySelectorAll('a, button, .clickable');
            touchTargets.forEach(target => {
                const rect = target.getBoundingClientRect();
                if (rect.height < 44 || rect.width < 44) {
                    target.style.minHeight = '44px';
                    target.style.minWidth = '44px';
                    target.style.display = 'inline-flex';
                    target.style.alignItems = 'center';
                    target.style.justifyContent = 'center';
                }
            });
            
            // Optimize map iframe for mobile
            const mapIframe = document.querySelector('.map-container iframe');
            if (mapIframe) {
                mapIframe.style.pointerEvents = 'auto';
                
                // Add touch-friendly controls message
                const touchMessage = document.createElement('div');
                touchMessage.style.cssText = `
                    position: absolute;
                    bottom: 10px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    z-index: 5;
                    pointer-events: none;
                `;
                touchMessage.textContent = 'Use two fingers to move the map';
                
                const mapContainer = mapIframe.parentElement;
                mapContainer.style.position = 'relative';
                mapContainer.appendChild(touchMessage);
                
                // Hide message after 3 seconds
                setTimeout(() => {
                    touchMessage.style.opacity = '0';
                    touchMessage.style.transition = 'opacity 0.5s';
                    setTimeout(() => touchMessage.remove(), 500);
                }, 3000);
            }
        }
    }
    
    // ========== PROGRESSIVE ENHANCEMENT ==========
    function initProgressiveEnhancement() {
        // Check for modern browser features
        const hasModernFeatures = (
            'IntersectionObserver' in window &&
            'requestAnimationFrame' in window &&
            CSS.supports('display', 'grid')
        );
        
        if (hasModernFeatures) {
            document.documentElement.classList.add('modern-browser');
            
            // Enable advanced animations
            document.querySelectorAll('.section').forEach((section, index) => {
                section.style.animationDelay = `${index * 0.1}s`;
            });
        } else {
            document.documentElement.classList.add('legacy-browser');
            
            // Provide fallbacks for older browsers
            console.log('Legacy browser detected, using fallback features');
        }
    }
    
    // ========== INITIALIZATION ==========
    function initialize() {
        try {
            // Core functionality
            initMobileNavigation();
            optimizeMapIframe();
            initScrollNavigation();
            
            // Performance optimizations
            optimizeImages();
            initPerformanceOptimizations();
            fixMobileViewportHeight();
            
            // User experience enhancements
            initTouchGestures();
            initMobileOptimizations();
            improveAccessibility();
            
            // Error handling and compatibility
            initErrorHandling();
            initProgressiveEnhancement();
            
            console.log('WebGIS mobile optimizations initialized successfully');
            
        } catch (error) {
            console.error('Error initializing WebGIS optimizations:', error);
            showErrorNotification('Failed to initialize some features. Please refresh the page.');
        }
    }
    
    // Start initialization
    initialize();
    
    // ========== UTILITY FUNCTIONS ==========
    
    // Debounce function for performance
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
    
    // Throttle function for scroll events
    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Smooth scroll polyfill for older browsers
    function smoothScrollPolyfill() {
        if (!('scrollBehavior' in document.documentElement.style)) {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/smoothscroll/1.4.10/SmoothScroll.min.js';
            document.head.appendChild(script);
        }
    }
    
    // Call polyfill if needed
    smoothScrollPolyfill();
    
    // ========== EXPORT FOR GLOBAL USE ==========
    window.WebGISMobile = {
        smoothScrollToElement,
        updateActiveNavLink,
        showErrorNotification,
        debounce,
        throttle,
        isInViewport
    };
});

// ========== CSS ANIMATION KEYFRAMES (Add to CSS) ==========
/*
Add these keyframes to your CSS file:

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
}

.section-visible {
    animation: fadeInUp 0.6s ease-out;
}

.mobile-device * {
    -webkit-tap-highlight-color: transparent;
}

.mobile-device *:hover {
    -webkit-transform: none !important;
    transform: none !important;
}
*/