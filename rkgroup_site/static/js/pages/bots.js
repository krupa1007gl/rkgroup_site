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
            
            // Получаем CSRF токен из cookie
            const csrftoken = getCookie('csrftoken');
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
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
                    let errorMsg = data.message || 'Ошибка отправки';
                    if (data.errors) {
                        errorMsg = Object.values(data.errors).join(', ');
                    }
                    messageDiv.innerHTML = '<div class="alert-error" style="background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 12px;">' + errorMsg + '</div>';
                    
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
    
    // Маска для телефона
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(phoneInput => {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            let formatted = '';
            if (value.length > 0) formatted = '+7';
            if (value.length > 1) formatted += ' (' + value.slice(1, 4);
            if (value.length > 4) formatted += ') ' + value.slice(4, 7);
            if (value.length > 7) formatted += '-' + value.slice(7, 9);
            if (value.length > 9) formatted += '-' + value.slice(9, 11);
            e.target.value = formatted;
        });
    });
    
    // Функция получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
