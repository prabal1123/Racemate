# racemate/racemate/settings_build.py
"""
Build-only Django settings for Vercel (static collection only).
Avoids importing sqlite3 and avoids loading Django apps.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "build-secret-key")

# Only include staticfiles so Django won't import models
INSTALLED_APPS = [
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# Use real urls UNLESS it causes import errors.
ROOT_URLCONF = "racemate.urls"

# If racemate.urls imports any app model at import-time, SWITCH to:
# ROOT_URLCONF = "racemate.urls_build"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Your real settings use BASE_DIR / "static"
STATICFILES_DIRS = [
    BASE_DIR / "static",        # racemate/static
]

# Allow dummy DB to avoid sqlite3 import
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

ALLOWED_HOSTS = ["*"]
USE_I18N = False
USE_TZ = False
