#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting Django Vercel Build ==="
cd /vercel/path0

# Install dependencies
python -m pip install --upgrade pip > /dev/null
python -m pip install -r requirements.txt > /dev/null

# Set environment
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

echo "Using DJANGO_SETTINGS_MODULE=racemate.racemate.settings"

# Test settings import
python -c "from django.conf import settings; print('Settings OK → STATIC_ROOT:', settings.STATIC_ROOT)"

# Collect static files — THIS IS THE FIX
echo "=== Running collectstatic ==="
python -m django collectstatic --no-input --clear --verbosity=2

# Final check
count=$(find staticfiles -type f 2>/dev/null | wc -l || echo 0)
echo "Collected $count static files"

if [ "$count" -eq 0 ]; then
  echo "ERROR: No static files collected!"
  exit 1
fi

echo "Build completed successfully!"