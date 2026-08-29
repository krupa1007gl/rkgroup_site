// static/js/pages/partners.js — форма «Стать партнёром»: live-валидация + AJAX-отправка

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('partner-form-el');
    if (!form) return;

    const messageDiv = form.querySelector('.form-message');
    const fields = Array.from(form.querySelectorAll('.form-input-custom'));

    const LABELS = {
        name: 'Укажите ваше имя',
        email: 'Укажите корректный email',
        company: 'Укажите компанию',
    };

    function isValid(field) {
        const value = field.value.trim();
        if (!value) return false;
        if (field.type === 'email') {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }
        return true;
    }

    function setFieldState(field, valid) {
        const group = field.closest('.form-group');
        field.classList.toggle('is-invalid', !valid);
        if (group) group.classList.toggle('has-error', !valid);

        let error = group ? group.querySelector('.field-error') : null;
        if (!valid) {
            if (!error && group) {
                error = document.createElement('div');
                error.className = 'field-error';
                group.appendChild(error);
            }
            if (error) error.textContent = LABELS[field.name] || 'Заполните поле';
        } else if (error) {
            error.remove();
        }
    }

    // Ошибка снимается по мере исправления, но не появляется до первой
    // попытки отправки — чтобы не ругаться на пустое поле сразу при заходе.
    fields.forEach(function(field) {
        field.addEventListener('input', function() {
            if (field.classList.contains('is-invalid')) {
                setFieldState(field, isValid(field));
            }
        });
        field.addEventListener('blur', function() {
            if (form.dataset.submitted === '1') {
                setFieldState(field, isValid(field));
            }
        });
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        form.dataset.submitted = '1';

        let firstInvalid = null;
        fields.forEach(function(field) {
            const valid = isValid(field);
            setFieldState(field, valid);
            if (!valid && !firstInvalid) firstInvalid = field;
        });

        if (firstInvalid) {
            firstInvalid.focus();
            return;
        }

        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = 'Отправка...';
        submitBtn.disabled = true;

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;

                if (data.status === 'ok') {
                    messageDiv.innerHTML = '<div class="alert-success-custom">' + data.message + '</div>';
                    form.reset();
                    form.dataset.submitted = '0';
                    fields.forEach(function(field) { setFieldState(field, true); });
                } else {
                    const errorText = data.errors
                        ? Object.values(data.errors).join(', ')
                        : (data.message || 'Ошибка отправки. Попробуйте позже.');
                    messageDiv.innerHTML = '<div class="alert-error-custom">' + errorText + '</div>';
                }
            })
            .catch(function() {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                messageDiv.innerHTML = '<div class="alert-error-custom">Ошибка соединения. Попробуйте позже.</div>';
            });
    });
});
