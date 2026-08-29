// static/js/pages/ailab.js — состояния страницы AI Lab (приглашение → SMS-верификация → живой бот) + демо-вкладки CRM/Excel

document.addEventListener('DOMContentLoaded', function() {
    const urls = window.AILAB_URLS || {};
    let verifiedPhone = '';

    function showPanel(id) {
        document.querySelectorAll('.ailab-panel').forEach(function(panel) {
            panel.classList.toggle('is-active', panel.id === id);
        });
    }

    function showMessage(form, text, isError) {
        const box = form.querySelector('.ailab-form-message');
        box.innerHTML = '<div class="' + (isError ? 'alert-error-custom' : 'alert-success-custom') + '">' + text + '</div>';
    }

    function getCookie(name) {
        const match = document.cookie.match('(^|;\\s*)' + name + '=([^;]*)');
        return match ? decodeURIComponent(match[2]) : '';
    }

    function postJson(url, payload) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        }).then(function(response) {
            return response.json().then(function(data) {
                return { ok: response.ok, data: data };
            });
        });
    }

    // ===== Состояние 1 (приглашение) → 2 (ввод телефона) =====
    const btnStartVerify = document.getElementById('btn-start-verify');
    if (btnStartVerify) {
        btnStartVerify.addEventListener('click', function() {
            showPanel('state-phone');
            document.querySelector('.ailab-stage').scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }

    // Маска телефона: принимает и "9161234567", и "89161234567"/"79161234567"
    const phoneInput = document.getElementById('phone-input');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let digits = e.target.value.replace(/\D/g, '');
            if (digits.length === 11 && (digits[0] === '7' || digits[0] === '8')) {
                digits = digits.slice(1);
            }
            digits = digits.slice(0, 10);

            let formatted = '+7';
            if (digits.length > 0) formatted += ' (' + digits.slice(0, 3);
            if (digits.length > 3) formatted += ') ' + digits.slice(3, 6);
            if (digits.length > 6) formatted += '-' + digits.slice(6, 8);
            if (digits.length > 8) formatted += '-' + digits.slice(8, 10);
            e.target.value = formatted;
        });
    }

    // Чекбокс согласия обязателен для активации кнопки
    const consentCheckbox = document.getElementById('consent-checkbox');
    const btnSendCode = document.getElementById('btn-send-code');
    if (consentCheckbox && btnSendCode) {
        consentCheckbox.addEventListener('change', function() {
            btnSendCode.disabled = !consentCheckbox.checked;
        });
    }

    // Отправка номера телефона
    const phoneForm = document.getElementById('phone-form');
    if (phoneForm) {
        phoneForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!consentCheckbox.checked) return;

            const phone = phoneInput.value;
            const website = phoneForm.querySelector('.ailab-honeypot').value;
            btnSendCode.disabled = true;

            postJson(urls.verifyStart, { phone: phone, website: website })
                .then(function(result) {
                    if (result.ok) {
                        verifiedPhone = phone;
                        document.getElementById('code-phone-display').textContent = phone;
                        showPanel('state-code');
                    } else {
                        showMessage(phoneForm, result.data.message || 'Ошибка отправки', true);
                        btnSendCode.disabled = !consentCheckbox.checked;
                    }
                })
                .catch(function() {
                    showMessage(phoneForm, 'Ошибка соединения. Попробуйте позже.', true);
                    btnSendCode.disabled = !consentCheckbox.checked;
                });
        });
    }

    // Проверка кода
    const codeForm = document.getElementById('code-form');
    if (codeForm) {
        codeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('code-input').value;

            postJson(urls.verifyConfirm, { phone: verifiedPhone, code: code })
                .then(function(result) {
                    if (result.ok && result.data.verified) {
                        document.getElementById('notify-phone').value = verifiedPhone;
                        showPanel('state-livebot');
                        checkBotStatus();
                    } else {
                        showMessage(codeForm, result.data.message || 'Неверный код', true);
                    }
                })
                .catch(function() {
                    showMessage(codeForm, 'Ошибка соединения. Попробуйте позже.', true);
                });
        });
    }

    // Статус живого бота
    function checkBotStatus() {
        if (!urls.botStatus) return;
        fetch(urls.botStatus)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                const comingSoon = document.getElementById('livebot-coming-soon');
                if (data.status !== 'coming_soon') {
                    comingSoon.style.display = 'none';
                }
            });
    }

    // "Сообщить о запуске"
    const notifyForm = document.getElementById('notify-form');
    if (notifyForm) {
        notifyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const payload = {
                name: document.getElementById('notify-name').value,
                phone: document.getElementById('notify-phone').value,
                website: notifyForm.querySelector('.ailab-honeypot').value,
            };
            postJson(urls.botNotifyMe, payload).then(function(result) {
                if (result.ok) {
                    showMessage(notifyForm, 'Спасибо! Сообщим, как только бот будет готов.', false);
                    notifyForm.querySelector('button[type="submit"]').disabled = true;
                } else {
                    showMessage(notifyForm, result.data.message || 'Ошибка отправки', true);
                }
            });
        });
    }

    // ===== Вкладки CRM / Excel =====
    const loadedTabs = {};

    function escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value == null ? '' : String(value);
        return div.innerHTML;
    }

    function renderDemoPanel(panel, data) {
        function renderSide(side, isAfter) {
            let inner = '<div class="ailab-demo-side' + (isAfter ? ' is-after' : '') + '">' +
                '<h4>' + escapeHtml(side.title) + '</h4>' +
                '<p>' + escapeHtml(side.description) + '</p>';

            if (side.items) {
                inner += '<div class="ailab-demo-items">';
                side.items.forEach(function(item) {
                    inner += '<div class="ailab-demo-item' + (item.changed ? ' is-changed' : '') + '">' +
                        '<span class="ailab-demo-label">' + escapeHtml(item.label) + '</span>' +
                        '<span class="ailab-demo-value">' + escapeHtml(item.value) + '</span>' +
                        '</div>';
                });
                inner += '</div>';
            }

            if (side.rows) {
                const changedCols = side.changed_cols || [];
                inner += '<div class="ailab-demo-table-wrap"><table class="ailab-demo-table"><tbody>';
                side.rows.forEach(function(row, rowIdx) {
                    inner += '<tr>' + row.map(function(cell, colIdx) {
                        if (rowIdx === 0) return '<th>' + escapeHtml(cell) + '</th>';
                        const changed = changedCols.indexOf(colIdx) !== -1;
                        return '<td' + (changed ? ' class="is-changed"' : '') + '>' + escapeHtml(cell) + '</td>';
                    }).join('') + '</tr>';
                });
                inner += '</tbody></table></div>';
            }

            inner += '</div>';
            return inner;
        }

        panel.innerHTML = '<div class="ailab-demo-grid">' +
            renderSide(data.before, false) +
            renderSide(data.after, true) +
            '</div>' +
            '<p class="ailab-demo-legend"><span class="ailab-demo-legend-swatch"></span> подсвечено то, что заполнил бот</p>';
    }

    document.querySelectorAll('.ailab-tab-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const tab = btn.dataset.tab;
            document.querySelectorAll('.ailab-tab-btn').forEach(function(b) { b.classList.toggle('is-active', b === btn); });
            document.querySelectorAll('.ailab-tab-panel').forEach(function(p) { p.classList.toggle('is-active', p.id === 'tab-' + tab); });

            const panel = document.getElementById('tab-' + tab);
            if (!loadedTabs[tab] && panel) {
                loadedTabs[tab] = true;
                fetch(panel.dataset.endpoint)
                    .then(function(r) { return r.json(); })
                    .then(function(data) { renderDemoPanel(panel, data); })
                    .catch(function() { panel.innerHTML = 'Не удалось загрузить демо.'; });
            }
        });
    });

    const firstTabPanel = document.getElementById('tab-crm');
    if (firstTabPanel) {
        loadedTabs.crm = true;
        fetch(firstTabPanel.dataset.endpoint)
            .then(function(r) { return r.json(); })
            .then(function(data) { renderDemoPanel(firstTabPanel, data); })
            .catch(function() { firstTabPanel.innerHTML = 'Не удалось загрузить демо.'; });
    }
});
