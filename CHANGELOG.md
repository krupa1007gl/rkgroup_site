# Рефакторинг бэкенда — итоговый отчёт

Ветка `backend-refactor` от `main`. Ниже — что сделано по каждому пункту
техзадания (A–D), что осталось как открытый вопрос для продукта, и как
проверить результат.

## Часть A — критичные проблемы безопасности

1. **SECRET_KEY** — старый хардкоженный ключ считается скомпрометированным,
   заменён. Теперь читается из `SECRET_KEY` в окружении (`os.environ['SECRET_KEY']`,
   упадёт при старте, если не задан — осознанно, чтобы не уйти в прод без ключа).
2. **DEBUG** — `os.environ.get('DEBUG', 'False') == 'True'`, по умолчанию `False`.
3. **ALLOWED_HOSTS** — список через запятую из `ALLOWED_HOSTS`, без `'*'`.
4. **db.sqlite3, visits.xlsx, leads_csv/, data/\*\*** — сняты с отслеживания
   (`git rm --cached`, файлы остаются на диске). **История git всё ещё
   содержит эти данные** — см. [SECURITY.md](SECURITY.md) с инструкцией по
   `git filter-repo`/BFG. Переписывание истории и force-push **не выполнены**
   автоматически — это отдельное разрушительное действие, требующее
   согласования с владельцем репозитория.
5. **`/leads/`, `/leads/update-status/`** — перенесены под
   `/admin/leads/` и `/admin/leads/update-status/`, обёрнуты в
   `admin.site.admin_view()` (редирект на `/admin/login/` без сессии
   staff-пользователя). Смена статуса логирует, кто и когда её выполнил.
6. **`/export-statistics/`** — дублирующий публичный роут удалён.
   Обнаружено: даже "административная" копия была зарегистрирована в
   `get_urls()` **без** `admin.site.admin_view()`, то есть тоже была
   фактически не защищена. Теперь обе проблемы устранены одним изменением
   — единственный маршрут `/admin/export-statistics/`, обёрнутый в `admin_view()`.
7. **python-dotenv** — `load_dotenv()` вызывается в начале `settings.py`,
   все секреты — через `.env` (не коммитится), добавлен `.env.example`
   с плейсхолдерами.

## Часть B — защита форм и rate limiting

8. **Rate limiting** — `RATELIMIT_ENABLED` через env (по умолчанию `True`),
   настроен `CACHES` (`LocMemCache`; TODO про `django-redis` для
   multi-worker деплоя в комментарии в `settings.py`). Исправлен
   `RateLimitMixin.dispatch`: раньше при превышении лимита для не-AJAX
   запроса он молча проваливался в обработку — теперь корректно возвращает
   429 в обоих случаях.
9. **Honeypot/rate limit на все формы** — раньше стояли только на
   консультации бота. Теперь на Callback/Contact/Partners (`main/views.py`)
   и AI Lab (по IP и по номеру телефона). Попутно найден и исправлен
   смежный баг: `HoneypotMixin.post()` при срабатывании для не-AJAX
   запроса вызывал `self.form_valid(None)`, что падало с `AttributeError`
   — теперь просто редиректит на `success_url`, ничего не сохраняя.
10. **CSV/Excel-инъекция формул** — `services/xlsx_export.py::escape_formula()`
    экранирует значения, начинающиеся с `=`, `+`, `-`, `@`, ведущим
    апострофом. Применяется в единственном оставшемся месте генерации
    Excel — экспорте статистики визитов.
11. **PartnerForm** — `PartnersPageView` переведён с чтения сырого
    `request.POST` на `main.forms.PartnerForm` (валидация email,
    обязательности полей).

## Часть C — уход от Excel как СУБД

12. **Модели вместо файлов** — новые приложения `leads` (модель `Lead`,
    объединяет callback/contact/consultation/partner/ai_lab — как раньше
    единый лист "Заявки") и `visits` (модель `Visit`). `services/excel_service.py`,
    `excel_base.py`, `visit_tracker.py` удалены полностью. Excel/CSV
    остались только как формат экспорта по требованию
    (`/admin/export-statistics/`, генерируется в памяти из `Visit`
    через `services/xlsx_export.py`).
13. **VisitTrackingMiddleware** — раньше на каждый GET синхронно
    перечитывал и целиком пересохранял xlsx-файл через openpyxl. Теперь
    — одна вставка через ORM (`Visit.objects.create()`). Буферизация/
    `bulk_create` сознательно не добавлены — по объёму трафика сайта
    это избыточное усложнение на данном этапе (зафиксировано в коммите).
14. **DATABASES** — читает `DATABASE_URL` (`dj-database-url`), если
    задан, иначе SQLite. TODO с инструкцией перехода на PostgreSQL при
    деплое; в репозитории уже был `migrate_to_postgres.py`
    (dumpdata/migrate/loaddata) — он совместим с этой схемой.
15. **Telegram-уведомления** — `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`
    заведены в `settings.py` через env (раньше читались через
    `getattr(..., None)`, но сама настройка нигде не была определена —
    уведомления не могли уйти в принципе). Проверено моком
    `requests.post`, что при заданных значениях сообщение реально
    отправляется.
16. **requirements.txt** — пересобран через `pip freeze` в чистом venv.
    Удалены версии, которых нет в PyPI, и неиспользуемые зависимости
    (google-api-python-client/gspread, pandas/numpy и их транзитивные
    хвосты — нигде не импортировались). `pip install -r requirements.txt`
    проверен с нуля в отдельном чистом venv.
17. **Тесты** — 41 тест на новый функционал (см. ниже "Как проверить").

## Часть D — бэкенд AI Lab

Новое приложение `ailab`. Фронтенда для страницы AI Lab не существовало
вовсе (ни шаблонов, ни статики) — контракт спроектирован с нуля, фронтенд
не тронут.

- **SMS-верификация**: `POST /ailab/verify/start/` (валидация номера на
  сервере через `common.validators.validate_phone`, honeypot, rate limit
  отдельно по IP и по номеру телефона) → `POST /ailab/verify/confirm/`
  (проверка кода только на сервере). Абстракция провайдера —
  `ailab/sms.py`: `BaseSmsProvider` / `StubSmsProvider`. Код фиксированный
  (`AILAB_STUB_OTP_CODE`, по умолчанию `"0000"`) — решение и его причина
  задокументированы в коде (`ailab/sms.py`). Время жизни кода и лимит
  попыток реализованы по-настоящему, чтобы контракт `send_code`/
  `verify_code` не менялся при подключении реального провайдера.
- Подтверждённый номер сохраняется как `Lead(lead_type='ai_lab',
  phone_verified=True, phone_verified_at=...)` — через тот же
  `leads.services.create_lead`, то же Telegram-уведомление, без
  отдельного канала.
- **Живой бот**: `GET /ailab/bot/status/` → `{"status": "coming_soon"}`,
  `POST /ailab/bot/notify-me/` сохраняет желающих узнать о запуске как
  лида. Единая точка входа — реальный вызов Twin API/виджета подключится
  сюда же без переделки контракта с фронтендом.
- **Сценарий-заглушка и вкладки CRM/Excel** — статичные JSON-фикстуры
  (`ailab/fixtures/*.json`), без обращения к БД или файлам пользователей.

## Известные ограничения и находки не по ТЗ

- В `bots/models.py` поля `created_at`/`updated_at` закомментированы, но
  `bots/migrations/0001_initial.py` всё ещё создаёт их в БД — `python
  manage.py makemigrations --check` показывает дрейф схемы. Это
  предшествовало данному рефакторингу и не относится к пунктам A–D, не
  тронуто.
- Форма обратного звонка (`CallbackCreateView`, `/callback/`) не имеет
  соответствующего HTML-шаблона на сайте — маршрут существует, но
  фронтенд его не вызывает. Не трогалось, вне контура задачи.
- Линтер (flake8/ruff) в репозитории `rkgroup_site` не настроен — прогнан
  только `python manage.py test` и `makemigrations --check`.

## Открытые вопросы (зафиксировать, не решено here)

- Выбор конкретного SMS-провайдера для реальной интеграции (кандидаты в
  `ailab/sms.py`: SMS.ru, SMSC.ru, Twilio).
- Формат интеграции с ботом на Twin (виджет/API/iframe) — нужно уточнить
  у платформы.
- Технически лиды AI Lab падают в общую таблицу `Lead` с пометкой
  источника `ai_lab`, уведомления идут в тот же Telegram — требует
  подтверждения бизнес-стороной, что это то самое место, куда команда
  ожидает получать эти лиды.
- Текст сценария-заглушки для состояния 1 AI Lab — сейчас
  placeholder-текст в `ailab/fixtures/scenario.json`, финальный текст
  должен согласовать продукт.
- Показывать ли страницу «Кейсы» в меню до появления первого настоящего
  кейса — решение продукта, бэкенд не участвует.

## Как проверить

```bash
cd rkgroup_site
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # и подставить SECRET_KEY, см. .env.example
python manage.py migrate
python manage.py test
python manage.py createsuperuser   # для доступа к /admin/leads/ и /admin/export-statistics/
python manage.py runserver
```

- `/admin/leads/` и `/admin/export-statistics/` без логина → редирект на
  `/admin/login/`.
- `POST /ailab/verify/start/ {"phone": "+7..."}`, затем
  `POST /ailab/verify/confirm/ {"phone": "+7...", "code": "0000"}`
  (код по умолчанию заглушки) → создаёт `Lead` с `phone_verified=True`.
