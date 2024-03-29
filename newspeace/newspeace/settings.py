"""
Django settings for newspeace project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

import db_info
import email_info

db = db_info.DATABASES['default']
key = db_info.KEY
email = email_info.DATABASES['default']


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = key['secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.newspeace.co.kr', 'm.newspeace.co.kr', 'newspeace.co.kr', 'localhost', '127.0.0.1']

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # 프론트엔드 주소
    # 다른 필요한 도메인 주소 추가
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "board",
    "news",
    "api",
    "notice",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "apscheduler",
    "enterprise",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "newspeace.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [f'{BASE_DIR}/templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "newspeace.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default' : {
#         'ENGINE': db['ENGINE'],
#         'NAME' : db['NAME'],
#         'USER' : db['USER'],
#         'PASSWORD' : db['PASSWORD'],
#         'HOST' : db['HOST'],
#         'PORT' : db['PORT'],
#         'OPTIONS' : {
#             'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
#         }
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

import os
STATIC_URL = "static/"
# STATICFILES_DIRS = [                            # 장고 개발 웹 서버에서만 사용하는 위치
#     os.path.join(BASE_DIR, 'newspeace', 'static'), 
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # 실제 서비스 할 때 사용하는 위치

MEDIA_URL = '/media/'                           # 가상 경로
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')    # media 파일 위치   # '\newspeace\media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# auth login,logout 환경 변수 설정해주기
LOGIN_REDIRECT_URL="/"

LOGOUT_REDIRECT_URL="/"

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

# 유저모델을 기본적인 auth에서 가져오는 것이 아니라,
# 내가 만든 앱(accounts)에 있는 User모델을 사용해달라는 의미
AUTH_USER_MODEL = 'accounts.User'

# 인증방식으로 토큰 사용
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# SMTP EMAIL gmail 계정
EMAIL_BACKEND = email['email_backend']
EMAIL_HOST = email['email_host']
EMAIL_USE_TLS = email['email_use_tls']
EMAIL_PORT = email['email_port']
EMAIL_HOST_USER = email['email_host_user']
EMAIL_HOST_PASSWORD = email['email_host_password']
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER