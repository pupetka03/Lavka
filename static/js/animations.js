// animations.js

class FXAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupLikeAnimations();
        this.setupHoverAnimations();
        this.setupFeedTabAnimations();
        this.setupModalAnimations();
        this.setupButtonAnimations();
        this.initializeAnimations();
    }

    // Анімації при скролі
    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Спостерігаємо за всіма елементами, що потребують анімації
        const animatedElements = document.querySelectorAll(
            '.publication-wrapper, .trend-item, .comment-item, .user-avatar, .tag'
        );
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }

    // Анімація елемента
    animateElement(element) {
        element.classList.add('in-view');
        
        // Додаткові ефекти для різних типів елементів
        if (element.classList.contains('publication-wrapper')) {
            this.animatePublication(element);
        } else if (element.classList.contains('trend-item')) {
            this.animateTrendItem(element);
        } else if (element.classList.contains('comment-item')) {
            this.animateComment(element);
        }
    }

    // Специфічні анімації для постів
    animatePublication(element) {
        element.style.transform = 'translateY(0)';
        element.style.opacity = '1';
        
        // Додаємо ефект при наведенні
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'translateY(-5px) scale(1.02)';
            element.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.1)';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = 'translateY(0) scale(1)';
            element.style.boxShadow = 'none';
        });
    }

    // Анімації для лайків
    setupLikeAnimations() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.like-button')) {
                this.animateLike(e.target.closest('.like-button'));
            }
        });
    }

    animateLike(button) {
        // Анімація кнопки
        button.classList.add('liked');
        button.style.transform = 'scale(1.3)';
        
        // Анімація счетчика
        const countElement = button.querySelector('.like-count');
        if (countElement) {
            countElement.style.transform = 'scale(1.5)';
            setTimeout(() => {
                countElement.style.transform = 'scale(1)';
            }, 300);
        }
        
        // Скидання стану
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 300);
        
        setTimeout(() => {
            button.classList.remove('liked');
        }, 1000);
    }

    // Анімації при наведенні
    setupHoverAnimations() {
        // Аватари
        document.querySelectorAll('.user-avatar').forEach(avatar => {
            avatar.addEventListener('mouseenter', () => {
                avatar.style.transform = 'scale(1.2) rotate(8deg)';
                avatar.style.filter = 'brightness(1.1)';
            });
            
            avatar.addEventListener('mouseleave', () => {
                avatar.style.transform = 'scale(1) rotate(0deg)';
                avatar.style.filter = 'brightness(1)';
            });
        });

        // Теги
        document.querySelectorAll('.tag').forEach(tag => {
            tag.addEventListener('mouseenter', () => {
                tag.style.transform = 'translateY(-3px) scale(1.1)';
                tag.style.textShadow = '0 4px 12px rgba(29, 161, 242, 0.6)';
            });
            
            tag.addEventListener('mouseleave', () => {
                tag.style.transform = 'translateY(0) scale(1)';
                tag.style.textShadow = 'none';
            });
        });

        // Кнопки в сайдбарі
        document.querySelectorAll('.sidebar-left nav a').forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.style.transform = 'translateX(10px) scale(1.05)';
            });
            
            link.addEventListener('mouseleave', () => {
                link.style.transform = 'translateX(0) scale(1)';
            });
        });
    }

    // Анімації для перемикача фідів
    setupFeedTabAnimations() {
        document.querySelectorAll('.feed-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.animateFeedTabSwitch(tab);
            });
            
            // Ефект при наведенні
            tab.addEventListener('mouseenter', () => {
                if (!tab.classList.contains('active')) {
                    tab.style.transform = 'translateY(-2px)';
                    tab.style.background = 'rgba(29, 161, 242, 0.1)';
                }
            });
            
            tab.addEventListener('mouseleave', () => {
                if (!tab.classList.contains('active')) {
                    tab.style.transform = 'translateY(0)';
                    tab.style.background = 'transparent';
                }
            });
        });
    }

    animateFeedTabSwitch(activeTab) {
        // Анімація активної вкладки
        activeTab.style.transform = 'scale(0.95)';
        setTimeout(() => {
            activeTab.style.transform = 'scale(1)';
        }, 150);

        // Анімація контенту фідів
        const feedId = activeTab.getAttribute('data-feed');
        const activeFeed = document.getElementById(feedId);
        
        if (activeFeed) {
            activeFeed.style.opacity = '0';
            activeFeed.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                activeFeed.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                activeFeed.style.opacity = '1';
                activeFeed.style.transform = 'translateY(0)';
            }, 50);
        }
    }

    // Анімації для модальних вікон
    setupModalAnimations() {
        this.setupSearchModalAnimations();
    }

    setupSearchModalAnimations() {
        const searchModal = document.getElementById('search-modal');
        const searchToggle = document.getElementById('search-toggle');
        const searchClose = document.getElementById('search-close');
        const searchInput = document.getElementById('search-input');

        if (searchToggle) {
            searchToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.openSearchModal();
            });
        }

        if (searchClose) {
            searchClose.addEventListener('click', () => {
                this.closeSearchModal();
            });
        }

        // Анімація поля вводу при фокусі
        if (searchInput) {
            searchInput.addEventListener('focus', () => {
                searchInput.style.transform = 'scale(1.02)';
                searchInput.style.boxShadow = '0 10px 30px rgba(29, 161, 242, 0.3)';
            });
            
            searchInput.addEventListener('blur', () => {
                searchInput.style.transform = 'scale(1)';
                searchInput.style.boxShadow = '0 0 0 3px rgba(29, 161, 242, 0.1)';
            });
        }
    }

    openSearchModal() {
        const searchModal = document.getElementById('search-modal');
        const modalContent = searchModal.querySelector('.bg-white');
        
        searchModal.classList.remove('hidden');
        
        // Анімація появи
        setTimeout(() => {
            searchModal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            modalContent.style.transform = 'scale(1)';
            modalContent.style.opacity = '1';
        }, 10);
        
        // Фокус на поле вводу
        const searchInput = document.getElementById('search-input');
        setTimeout(() => searchInput.focus(), 200);
    }

    closeSearchModal() {
        const searchModal = document.getElementById('search-modal');
        const modalContent = searchModal.querySelector('.bg-white');
        
        modalContent.style.transform = 'scale(0.9)';
        modalContent.style.opacity = '0';
        searchModal.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        
        setTimeout(() => {
            searchModal.classList.add('hidden');
            const searchInput = document.getElementById('search-input');
            searchInput.value = '';
        }, 300);
    }

    // Анімації для кнопок
    setupButtonAnimations() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.post-button')) {
                this.animateButton(e.target.closest('.post-button'));
            }
        });

        // Ефект ripple для всіх кнопок
        document.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.createRippleEffect(e, button);
            });
        });
    }

    animateButton(button) {
        button.style.transform = 'scale(0.95)';
        button.style.boxShadow = '0 5px 15px rgba(29, 161, 242, 0.4)';
        
        setTimeout(() => {
            button.style.transform = 'scale(1)';
            button.style.boxShadow = '0 10px 25px rgba(29, 161, 242, 0.3)';
        }, 150);
    }

    createRippleEffect(event, button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // Ініціалізація всіх анімацій
    initializeAnimations() {
        // Додаємо CSS для ripple ефекту
        this.injectRippleStyles();
        
        // Запускаємо початкові анімації
        setTimeout(() => {
            document.querySelectorAll('.publication-wrapper, .trend-item, .comment-item')
                .forEach((el, index) => {
                    el.style.animationDelay = (index * 0.1) + 's';
                    el.classList.add('in-view');
                });
        }, 500);
    }

    injectRippleStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
            }
            
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            /* Додаткові анімації для JavaScript */
            .publication-wrapper, .trend-item, .comment-item {
                transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .in-view {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Додаткові утиліти
    animateNewPost(element) {
        element.classList.add('new-post-added');
        element.style.animation = 'bounceIn 0.8s ease-out, glow 2s ease-in-out';
        
        setTimeout(() => {
            element.classList.remove('new-post-added');
            element.style.animation = '';
        }, 2000);
    }

    shakeElement(element) {
        element.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }

    pulseElement(element) {
        element.style.animation = 'pulse 2s infinite';
        setTimeout(() => {
            element.style.animation = '';
        }, 2000);
    }
}

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.fxAnimations = new FXAnimations();
});

// Експорт для використання в інших файлах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FXAnimations;
}