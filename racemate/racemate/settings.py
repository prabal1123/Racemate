# # racemate/settings.py (full file, with AccountMiddleware included)
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent

# # Quick-start dev settings
# SECRET_KEY = 'django-insecure-nb$is1kj1zfah^9y09$dw$3ghiml3cf8yqs(vbv@7v9ryoyvu+'
# DEBUG = True
# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# # Sites framework
# SITE_ID = 1

# # Application definition
# INSTALLED_APPS = [
#     # Django contrib apps
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',

#     # Sites (required by allauth)
#     'django.contrib.sites',

#     # Your app(s)
#     'accounts',
#     'app_admin',

#     # django-allauth and providers
#     'allauth',
#     'allauth.account',
#     'allauth.socialaccount',
#     'allauth.socialaccount.providers.google',  # add providers you want
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',

#     # allauth requires this middleware to be present
#     # add it here (must be present before AuthenticationMiddleware)
#     'allauth.account.middleware.AccountMiddleware',

#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'racemate.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         # project-level templates dir
#         'DIRS': [BASE_DIR / 'templates'],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 # required by allauth:
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 # default Django context processors
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'racemate.wsgi.application'

# # Database (sqlite for dev)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# # Authentication backends (required for allauth)
# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',  # admin login
#     'allauth.account.auth_backends.AuthenticationBackend',
# ]

# # django-allauth recommended defaults for dev
# ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'optional'
# ACCOUNT_USERNAME_REQUIRED = True
# LOGIN_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/'
# ACCOUNT_SESSION_REMEMBER = True

# # Email backend for development — prints emails to console
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# # Password validation (defaults)
# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
# ]

# # Internationalization
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# # Static files
# STATIC_URL = 'static/'
# STATICFILES_DIRS = [BASE_DIR / "static"]

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# # racemate/settings.py
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-nb$is1kj1zfah^9y09$dw$3ghiml3cf8yqs(vbv@7v9ryoyvu+'
# DEBUG = True
# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# SITE_ID = 1

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'django.contrib.sites',
#     'django.contrib.humanize',

#     'accounts',
#     'app_admin',
#     'app_bib',
#     'django_filters',
#     'app_results',
    

#     'allauth',
#     'allauth.account',
#     'allauth.socialaccount',
#     'allauth.socialaccount.providers.google',
     
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'allauth.account.middleware.AccountMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'racemate.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [BASE_DIR / 'templates'],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'racemate.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
#     'allauth.account.auth_backends.AuthenticationBackend',
# ]

# ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'optional'
# ACCOUNT_USERNAME_REQUIRED = True
# LOGIN_REDIRECT_URL = 'login'
# LOGOUT_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/'
# # ACCOUNT_LOGOUT_ON_GET = True
# ACCOUNT_SESSION_REMEMBER = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = 'static/'
# STATICFILES_DIRS = [BASE_DIR / "static"]

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# racemate/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-nb$is1kj1zfah^9y09$dw$3ghiml3cf8yqs(vbv@7v9ryoyvu+'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Safe detection of whitenoise so we don't error if package isn't installed
try:
    import whitenoise  # type: ignore
    WHITENOISE_AVAILABLE = True
except Exception:
    WHITENOISE_AVAILABLE = False

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    'accounts',
    'app_admin',
    'app_bib',
    'django_filters',
    'app_results',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# MIDDLEWARE: keep your existing order; insert WhiteNoise only if available
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

if WHITENOISE_AVAILABLE:
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE += [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'racemate.urls'

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

WSGI_APPLICATION = 'racemate.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USERNAME_REQUIRED = True
LOGIN_REDIRECT_URL = 'login'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC + MEDIA (non-invasive additions)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

if WHITENOISE_AVAILABLE:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "mediafiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
