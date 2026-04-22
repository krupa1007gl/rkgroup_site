// static/js/pages/bots.js - Скрипты для страниц с ботами

document.addEventListener('DOMContentLoaded', function() {
    // Обработка формы консультации на странице детального бота
    const consultationForm = document.getElementById('consultation-form');
    
    if (consultationForm) {
        consultationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<span>⏳ Отправка...</span>';
            submitBtn.disabled = true;
            
            const formData = new FormData(this);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            
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
                    messageDiv.innerHTML = '<div class="alert-success" style="background: #d1fae5; color: #065f46; padding: 12px; border-radius: 12px;">' + data.message + '</div>';
                    this.reset();
                    
                    setTimeout(() => {
                        messageDiv.innerHTML = '';
                    }, 3000);
                } else if (data.status === 'error') {
                    messageDiv.innerHTML = '<div class="alert-error" style="background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 12px;">' + (data.message || 'Ошибка отправки') + '</div>';
                    
                    setTimeout(() => {
                        messageDiv.innerHTML = '';
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                
                const messageDiv = consultationForm.querySelector('.form-message');
                messageDiv.innerHTML = '<div class="alert-error" style="background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 12px;">Ошибка соединения. Попробуйте позже.</div>';
                
                setTimeout(() => {
                    messageDiv.innerHTML = '';
                }, 3000);
            });
        });
    }
});