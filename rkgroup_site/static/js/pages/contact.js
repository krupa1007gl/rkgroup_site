// static/js/pages/contact.js - Скрипты для страницы контактов

document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submit-contact-btn');
            const originalText = submitBtn.innerHTML;
            
            // Анимация загрузки
            submitBtn.innerHTML = '<span>⏳ Отправка...</span>';
            submitBtn.disabled = true;
            
            const formData = new FormData(this);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            
            if (!csrfToken) {
                console.error('CSRF token not found');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                return;
            }
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                
                const messageDiv = this.querySelector('.form-message');
                
                if (data.status === 'ok') {
                    messageDiv.innerHTML = '<div class="alert-success-custom"><i class="fas fa-check-circle" style="margin-right: 8px;"></i> ' + data.message + '</div>';
                    this.reset();
                    
                    setTimeout(() => {
                        const alert = messageDiv.querySelector('.alert-success-custom');
                        if (alert) {
                            alert.style.opacity = '0';
                            alert.style.transform = 'translateY(-10px)';
                            setTimeout(() => {
                                messageDiv.innerHTML = '';
                            }, 300);
                        }
                    }, 4000);
                } else if (data.status === 'error') {
                    messageDiv.innerHTML = '<div class="alert-error-custom"><i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i> ' + (data.message || 'Ошибка отправки. Попробуйте позже.') + '</div>';
                    
                    setTimeout(() => {
                        const alert = messageDiv.querySelector('.alert-error-custom');
                        if (alert) {
                            alert.style.opacity = '0';
                            alert.style.transform = 'translateY(-10px)';
                            setTimeout(() => {
                                messageDiv.innerHTML = '';
                            }, 300);
                        }
                    }, 4000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                
                const messageDiv = contactForm.querySelector('.form-message');
                messageDiv.innerHTML = '<div class="alert-error-custom"><i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i> Ошибка соединения. Попробуйте позже.</div>';
                
                setTimeout(() => {
                    const alert = messageDiv.querySelector('.alert-error-custom');
                    if (alert) {
                        alert.style.opacity = '0';
                        alert.style.transform = 'translateY(-10px)';
                        setTimeout(() => {
                            messageDiv.innerHTML = '';
                        }, 300);
                    }
                }, 4000);
            });
        });
    }
});