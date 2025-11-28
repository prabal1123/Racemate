# racemate/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-nb$is1kj1zfah^9y09$dw$3ghiml3cf8yqs(vbv@7v9ryoyvu+'
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "racemate-silk.vercel.app",
    "racemate-j57dwy1q0-prabal1123s-projects.vercel.app",
    "*",
]

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

    # project apps
    # 'accounts',
    # 'app_admin',
    # 'app_bib',
    # 'django_filters',
    # 'app_results',

    'racemate.accounts',
    'racemate.app_admin',
    'racemate.app_bib',
    'racemate.app_results',
    'racemate.pages',

    # auth/social
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',            # serve static files in production
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

# -------------------------
# Static files
# -------------------------
# URL to use when referring to static files
STATIC_URL = "/static/"

# Where collectstatic will collect static files for deployment (Vercel build uses this)

#STATIC_ROOT = BASE_DIR / "staticfiles"
# Static files

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / "static",   # ← points to project-root/static/
]
# Where your source static files live (so collectstatic can find them)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Use a simple storage backend during build to avoid remote/storage-related failures.
# You can switch to a manifest/whitenoise storage later if you want cache-busted filenames.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# -------------------------
# Media files (optional)
# -------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# # racemate/settings.py
# from pathlib import Path
# import os,re

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-nb$is1kj1zfah^9y09$dw$3ghiml3cf8yqs(vbv@7v9ryoyvu+'
# #DEBUG = True
# DEBUG = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")
# ALLOWED_HOSTS = ["127.0.0.1", "localhost","racemate-silk.vercel.app", "racemate-j57dwy1q0-prabal1123s-projects.vercel.app", "*"]

# # DEBUG — temporarily print what the runtime sees (remove after debugging)

# print("DEBUG: ENV ALLOWED_HOSTS =", os.environ.get("ALLOWED_HOSTS"))
# print("DEBUG: FINAL ALLOWED_HOSTS =", ALLOWED_HOSTS)


# env_hosts = os.environ.get("ALLOWED_HOSTS", "")
# if env_hosts:
#     for host in env_hosts.split(","):
#         host = host.strip()
#         if host.startswith("*."):
#             # convert wildcard into regex pattern
#             pattern = r".*\." + re.escape(host[2:]) + r"$"
#             ALLOWED_HOSTS.append(pattern)
#         else:
#             ALLOWED_HOSTS.append(host)

# # Safe detection of whitenoise so we don't error if package isn't installed
# try:
#     import whitenoise  # type: ignore
#     WHITENOISE_AVAILABLE = True
# except Exception:
#     WHITENOISE_AVAILABLE = False

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

# # MIDDLEWARE: keep your existing order; insert WhiteNoise only if available
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
# ]

# if WHITENOISE_AVAILABLE:
#     MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

# MIDDLEWARE += [
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

# # STATIC + MEDIA (non-invasive additions)
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR / "static"]
# STATIC_ROOT = BASE_DIR / "staticfiles"

# if WHITENOISE_AVAILABLE:
#     STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / "mediafiles"

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
