// static/js/pages/faq.js — простой accordion для FAQ

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.faq-item').forEach(function(item) {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', function() {
            const wasOpen = item.classList.contains('open');
            document.querySelectorAll('.faq-item.open').forEach(function(openItem) {
                openItem.classList.remove('open');
            });
            if (!wasOpen) {
                item.classList.add('open');
            }
        });
    });
});
