import os

from amabase import __prog__
from amabase.utils import get_linux_default_gateway_ip, get_logging_config

# Paths and security
# https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

DATA_DIR = None # Automatically set by settings.configure()

DEBUG = None # Automatically set by settings.configure()

SECRET_KEY = None  # Automatically generated and stored in the configuration SQLite database

DOMAIN_NAME = None

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',') if os.environ.get('ALLOWED_HOSTS') else ['127.0.0.1', 'localhost', '__domain_name__']

CSRF_TRUSTED_ORIGINS = None  # Automatically generated from ALLOWED_HOSTS

INTERNAL_IPS = ['127.0.0.1'] # used by debug_toolbar and for django.template.context_processors.debug
if os.path.exists('/.dockerenv'):
    INTERNAL_IPS.append('172.17.0.1')    
    if (gateway := get_linux_default_gateway_ip()) and not gateway in INTERNAL_IPS:
        INTERNAL_IPS.append(gateway)


# Application definition
# https://docs.djangoproject.com/en/5.2/ref/applications/

ASGI_APPLICATION = 'amabase.django.asgi.application'

ROOT_URLCONF = 'amabase.django.urls'

APPS = [
    'amabase.cmdb',
    'amabase.ipam',
]

USE_GIS = None  # Determined automatically

INSTALLED_APPS = [
    'daphne',   # `runserver` command
    'channels', # `runworker` command
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    '__gis__',  # automatically substituted by 'django.contrib.gis' if USE_GIS setting is true
    'django.contrib.admin',
    'amabase.base', # before `admin` because it may override templates TODO?
    '__apps__', # automatically substituted by APPS setting
    'django_filters',
    'debug_toolbar',
    'import_export',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    # 'default' will be set to conf db by default
}


# Authentication
# https://docs.djangoproject.com/en/5.2/topics/auth/customizing/

AUTH_USER_MODEL = 'base.User'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

USE_I18N = True
LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images) and data files
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = '{DATA_DIR}/static'

MEDIA_URL = 'media/'
MEDIA_ROOT = '{DATA_DIR}/media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Logging
# https://docs.djangoproject.com/en/5.2/ref/settings/#logging

LOGGING = get_logging_config()


# Amabase-specifics

FAVICON_URL = 'base/favicon.ico'

SITE_TITLE = None

SITE_INDEX_HEADER = "Home"
