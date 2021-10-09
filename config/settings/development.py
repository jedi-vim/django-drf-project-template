import os

from .base import *

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ecommerce_backend_db',
        'USER': 'ecommerce_backend_user',
        'PASSWORD': 'IWKdrWWnc6XA39pgX6PU',
        'HOST': 'localhost',
        'PORT': '5453'
    }
}
