
# racemate/racemate/settings_build.py
"""
Build-only settings for Vercel collectstatic.
Do NOT use at runtime.
"""

from pathlib import Path
import os

# settings_build.py path: <repo_root>/racemate/racemate/settings_build.py
HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[2]    # -> <repo_root>
APP_BASE = HERE.parents[1]        # -> <repo_root>/racemate (where racemate/static lives)

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "build-secret-key")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "racemate.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

# Vercel expects the build output directory at the repository root: <repo_root>/staticfiles
STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_ROOT / "staticfiles"

# Source static dirs: repo_root/static (if any) and repo_root/racemate/static (your actual path)
STATICFILES_DIRS = [
    PROJECT_ROOT / "static",
    APP_BASE / "static",
]

DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}

ALLOWED_HOSTS = ["*"]
USE_I18N = False
USE_TZ = False
                