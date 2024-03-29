"""
Django settings for raildb project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, 'env', '.env'))

# このサイトの URL
BASE_URL = env('BASE_URL')
CSRF_TRUSTED_ORIGINS = [env('CSRF_TRUSTED_ORIGINS')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # third party
    'discord_logging',
    'django_bootstrap5',
    'django_celery_results',
    'django_select2',
    'import_export',
    'ordered_model',
    # raildb
    'ekidata',
    'home',
    'library',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'raildb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'generic', 'templates')],
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

WSGI_APPLICATION = 'raildb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': env.db(engine='django.contrib.gis.db.backends.postgis')
}


# Substituting a custom User model¶
# https://docs.djangoproject.com/en/4.1/topics/auth/customizing/#auth-custom-user

AUTH_USER_MODEL = 'home.User'


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_ROOT = 'static/'

STATIC_URL = env('STATIC_URL')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'generic', 'static')
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache
# https://docs.djangoproject.com/en/4.1/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://raildb_cache:6379'
    }
}


# Auth
# https://docs.djangoproject.com/en/4.1/ref/settings/#login-redirect-url

LOGIN_REDIRECT_URL = 'home:index'
LOGIN_URL = 'home:auth_signin'


# Email
# https://docs.djangoproject.com/en/4.1/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env('EMAIL_PORT')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = env('EMAIL_USE_TLS')
    EMAIL_SSL_KEYFILE = env('EMAIL_SSL_KEYFILE')
    EMAIL_SSL_CERTFILE = env('EMAIL_SSL_CERTFILE')

# Logging
# https://docs.djangoproject.com/en/4.1/topics/logging/#disabling-logging-configuration
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format':
                    '{levelname} {asctime} {module} '
                    '{process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'DEBUG',
                'filename': '/var/log/raildb/debug.log',
                'when': 'd',
                'formatter': 'verbose'
            },
            'discord': {
                'class': 'discord_logging.handler.DiscordHandler',
                'level': 'ERROR',
                'service_name': 'RailDB',
                'webhook_url': env('DISCORD_WEBHOOK_LOGGER')
            }
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'discord'],
                'propagate': True,
            },
        }
    }

# Celery
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

CELERY_BROKER_URL = 'redis://raildb_cache'
CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_EXTENDED = True


# django-select2
# https://django-select2.readthedocs.io/en/latest/

SELECT2_CACHE_BACKEND = 'default'


# django-import-export
# https://django-import-export.readthedocs.io/en/latest/index.html
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.CacheStorage'


# Email トークンの有効時間を指定（分単位）
EMAIL_TOKEN_EXP = 5
