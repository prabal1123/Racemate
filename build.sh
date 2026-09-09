#!/usr/bin/env bash
set -euo pipefail

echo "=== build.sh starting ==="
pwd
ls -la

# Install Python dependencies required for collectstatic
if [ -f requirements.txt ]; then
  echo "Installing Python requirements..."
  python -m pip install --upgrade pip setuptools wheel
  python -m pip install -r requirements.txt --no-cache-dir
fi

# Build frontend assets first (Tailwind/Vite/etc.)
if [ -f package.json ]; then
  echo "Building frontend assets..."
  npm ci || true

  if npm run | grep -q " build"; then
    npm run build || echo "⚠️ npm run build failed (continuing)"
  else
    echo "⚠️ No 'build' script found in package.json"
  fi
fi

# Set Python path
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
echo "PYTHONPATH=$PYTHONPATH"

# Build-only settings (to avoid sqlite3 errors)
export DJANGO_SETTINGS_MODULE=racemate.racemate.settings_build
echo "Using DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Make output directory (Vercel will take from here)
mkdir -p staticfiles

# Run collectstatic
echo "Running collectstatic..."
python manage.py collectstatic --noinput --clear || {
  echo "⚠️ collectstatic failed (non-fatal)"
}

echo "=== staticfiles generated ==="
ls -la staticfiles/

echo "=== build.sh finished ==="
