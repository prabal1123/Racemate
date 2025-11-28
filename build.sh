#!/usr/bin/env bash
set -eux

# Ensure we run from the repository root (Vercel's repo root is /vercel/path0)
cd "$(pwd)"

# Make sure Python tooling is up-to-date
python -m pip install --upgrade pip setuptools wheel

# Install python deps
python -m pip install -r requirements.txt

# If you use node/tailwind to build CSS, run it here BEFORE collectstatic.
# This ensures static/css/base.css exists when collectstatic runs.
if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    npm ci
    npm run build
  elif command -v yarn >/dev/null 2>&1; then
    yarn install --frozen-lockfile
    yarn build
  fi
fi

# Ensure Python can import your project package.
# /vercel/path0 is Vercel's repo root at runtime; add it explicitly to PYTHONPATH.
export PYTHONPATH="${PYTHONPATH:-}:/vercel/path0"

# Make sure Django uses the project's settings module.
export DJANGO_SETTINGS_MODULE="racemate.settings"

# Run collectstatic into STATIC_ROOT (staticfiles/)
python manage.py collectstatic --noinput
