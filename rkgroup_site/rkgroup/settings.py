import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'bots',
    'cases',
    'news',
    'leads',
    'visits',
]

MIDDLEWARE = [
    'middleware.VisitTrackingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rkgroup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rkgroup.wsgi.application'

# Лиды и статистика визитов хранятся в этой БД (см. приложения leads, visits).
# SQLite — приемлемый вариант для разработки и небольшой нагрузки, но не
# рассчитан на конкурентную запись при реальном трафике.
# TODO: при деплое задать DATABASE_URL (например
# postgres://user:password@host:5432/dbname) и перейти на PostgreSQL —
# psycopg2-binary и dj-database-url уже есть в зависимостях.
if os.environ.get('DATABASE_URL'):
    DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'])}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== RATE LIMITING ==========
RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True') == 'True'

# LocMemCache хватает для одного воркера. Для деплоя с несколькими
# процессами/воркерами лимиты не будут общими между процессами —
# в этом случае стоит подключить django-redis и Redis.
# TODO: перейти на django-redis (CACHES['default']['BACKEND'] =
# 'django_redis.cache.RedisCache'), если потребуется multi-worker деплой.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ========== НАСТРОЙКИ ДЛЯ ФАЙЛОВ ==========
DATA_DIR = os.environ.get('DATA_DIR', str(Path(BASE_DIR).parent / 'data'))

LEADS_DIR = os.path.join(DATA_DIR, 'leads')
VISITS_DIR = os.path.join(DATA_DIR, 'visits')
BACKUPS_DIR = os.path.join(DATA_DIR, 'backups')

os.makedirs(LEADS_DIR, exist_ok=True)
os.makedirs(VISITS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# ========== ЛОГИРОВАНИЕ ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'services': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'middleware': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
#========== НАСТРОЙКИ EXCEL ==========
LEADS_MAX_RECORDS_PER_FILE = 100