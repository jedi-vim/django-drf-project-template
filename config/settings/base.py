import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).parents[2]

SECRET_KEY = '@8*e_7dwlyn3!v3a*+fhi8a%96nl!_x%)ub=25dvfggu%1oyx^'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'ecommerce_backend.purchases',
    'ecommerce_backend.reports',
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [

    ],
}

MIDDLEWARE = [
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
        'default': dj_database_url.config(env='DATABASE_URL'),
}


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
