#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting Django Vercel Build ==="
cd /vercel/path0

# Install dependencies
python -m pip install --upgrade pip > /dev/null
python -m pip install -r requirements.txt > /dev/null

# Ensure project root is in path
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"

# Hardcode settings module (your structure is known)
export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

echo "Using DJANGO_SETTINGS_MODULE=racemate.racemate.settings"

# Test import
python -c "import django; from django.conf import settings; print('Settings OK:', settings.STATIC_ROOT)" || exit 1

# Collect static files
echo "=== Running collectstatic ==="
mkdir -p staticfiles
python manage.py collectstatic --no-input --clear --verbosity=2

# Final check
count=$(find staticfiles -type f 2>/dev/null | wc -l)
echo "Collected $count static files"

if [ "$count" -eq 0 ]; then
  echo "ERROR: No files collected!"
  exit 1
fi

echo "Build successful! Static files ready at /staticfiles"