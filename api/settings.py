import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')vo$dy^%t#dx!nv(nwy*)(*x9cb26cbnfa#vvj0!(drari-01t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*','127.0.0.1','localhost','3.18.22.188','xn--salonayr-zkb.com']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:3000',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://127.0.0.1:3000',
]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    'django_crontab',

    'hall',
    'user',
    'slot',
    'city',
    'reservation',
    'portion',

    'storages',
]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

]


ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wedding2',
        'USER': 'gakko',
        'PASSWORD':'1221',
    }
}
'''
0 0 utc+3 icin bilgisayar loca timeina gore calisir.AWS de date +'%z %Z' konsolda bunu yazarak timezone ogren 
'''
CRONJOBS = [
    ('*/1 * * * *', 'reservation.cron.update_reservation'),
    ('0 21 * * *', 'slot.cron.update_slot'),
    ('30 12 * * *', 'reservation.cron.notify_duration'),
    ('24 19 * * *', 'reservation.cron.delete_photos_not_extended'),
    ('0 0 1 * *', 'reservation.cron.update_count_of_visit'),
]

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'user.User'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

HALL_MODEL = 'hall.Hall'

USE_L10N = True



REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
MEDIA_URL = '/images/'
STATIC_URL = '/static/'

# Path where media is stored
MEDIA_ROOT = os.path.join(BASE_DIR,'build/static/images')


AWS_ACCESS_KEY_ID = 'AKIAVGK4LKIZG4NCGCXM'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'my-wedding-hall-project'
AWS_STORAGE_BUCKET_NAME_RESIZED = 'my-wedding-hall-project-resized'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
