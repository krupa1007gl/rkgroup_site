// static/js/base.js - Базовые скрипты с премиальными анимациями

document.addEventListener('DOMContentLoaded', function() {
    // ========== ПЛАВНАЯ ЗАГРУЗКА ==========
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.6s ease';
    setTimeout(() => { document.body.style.opacity = '1'; }, 100);

    // ========== ПЕЧАТНАЯ МАШИНКА ДЛЯ HERO (фиксированная высота строки) ==========
    const typedElement = document.getElementById('typed-text');
    if (typedElement) {
        const words = ['меняют бизнес', 'увеличивают прибыль', 'автоматизируют всё'];
        let wordIndex = 0, charIndex = 0, isDeleting = false;
        
        // Устанавливаем начальное значение, чтобы элемент не был пустым
        typedElement.textContent = 'меняют бизнес';
        
        function typeEffect() {
            const currentWord = words[wordIndex];
            if (isDeleting) {
                typedElement.textContent = currentWord.substring(0, charIndex - 1);
                charIndex--;
            } else {
                typedElement.textContent = currentWord.substring(0, charIndex + 1);
                charIndex++;
            }
            if (!isDeleting && charIndex === currentWord.length) {
                isDeleting = true;
                setTimeout(typeEffect, 2000);
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex = (wordIndex + 1) % words.length;
                setTimeout(typeEffect, 500);
            } else {
                setTimeout(typeEffect, isDeleting ? 50 : 100);
            }
        }
        typeEffect();
    }

    // ========== 3D СФЕРА НА HERO (Canvas) ==========
    const canvas = document.getElementById('heroCanvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width = canvas.clientWidth;
        let height = canvas.clientHeight;
        canvas.width = width;
        canvas.height = height;

        let particles = [];
        for (let i = 0; i < 80; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                radius: Math.random() * 2 + 1,
                alpha: Math.random() * 0.5 + 0.2,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5
            });
        }

        function animateSphere() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.x += p.speedX;
                p.y += p.speedY;
                if (p.x < 0) p.x = width;
                if (p.x > width) p.x = 0;
                if (p.y < 0) p.y = height;
                if (p.y > height) p.y = 0;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(59, 130, 246, ${p.alpha})`;
                ctx.fill();
            });
            requestAnimationFrame(animateSphere);
        }
        animateSphere();
        window.addEventListener('resize', () => {
            width = canvas.clientWidth;
            height = canvas.clientHeight;
            canvas.width = width;
            canvas.height = height;
        });
    }

    // ========== СЧЁТЧИКИ ПРИ ПРОКРУТКЕ ==========
    const counters = document.querySelectorAll('.counter-number');
    const observerOptions = { threshold: 0.3, rootMargin: '0px' };

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-target'));
                if (!el.classList.contains('counted')) {
                    el.classList.add('counted');
                    let current = 0;
                    const increment = target / 50;
                    const updateCounter = () => {
                        current += increment;
                        if (current < target) {
                            el.textContent = Math.floor(current);
                            requestAnimationFrame(updateCounter);
                        } else {
                            el.textContent = target;
                        }
                    };
                    updateCounter();
                }
                counterObserver.unobserve(el);
            }
        });
    }, observerOptions);

    counters.forEach(counter => counterObserver.observe(counter));

    // ========== ПОЯВЛЕНИЕ ЭЛЕМЕНТОВ ПРИ СКРОЛЛЕ ==========
    const fadeElements = document.querySelectorAll('.fade-up, .card, .bot-card, .case-card, .news-card, .stat-card, .stage-card');
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                scrollObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px' });

    fadeElements.forEach(el => scrollObserver.observe(el));

    // ========== МОБИЛЬНОЕ МЕНЮ ==========
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.nav');
    
    if (mobileBtn) {
        mobileBtn.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }
    
    // ========== ВЫПАДАЮЩИЕ МЕНЮ ==========
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            if (window.innerWidth > 768) this.classList.add('open');
        });
        dropdown.addEventListener('mouseleave', function() {
            if (window.innerWidth > 768) this.classList.remove('open');
        });
        
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) {
            toggle.addEventListener('click', function(e) {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    e.stopPropagation();
                    dropdown.classList.toggle('open');
                }
            });
        }
    });
    
    // Закрытие меню при клике на ссылку
    const navLinks = document.querySelectorAll('.dropdown-item, .nav-link:not(.dropdown-toggle)');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                nav.classList.remove('active');
                dropdowns.forEach(d => d.classList.remove('open'));
            }
        });
    });
    
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!nav.contains(e.target) && mobileBtn && !mobileBtn.contains(e.target)) {
                nav.classList.remove('active');
                dropdowns.forEach(d => d.classList.remove('open'));
            }
        }
    });
    
    // Плавный скролл
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!' && href !== '') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
    
    // Модальные окна
    const modals = document.querySelectorAll('.modal');
    const modalTriggers = document.querySelectorAll('.js-open-modal');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'block';
                setTimeout(() => modal.classList.add('show'), 10);
            }
        });
    });
    
    const modalCloses = document.querySelectorAll('.modal__close');
    modalCloses.forEach(close => {
        close.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.remove('show');
                setTimeout(() => modal.style.display = 'none', 300);
            }
        });
    });
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('show');
            setTimeout(() => e.target.style.display = 'none', 300);
        }
    });
});