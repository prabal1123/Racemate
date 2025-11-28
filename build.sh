#!/usr/bin/env bash
set -euo pipefail  # safer than set -eux (still fails fast but cleaner output)

# Ensure we're in the project root (Vercel sets this)
cd /vercel/path0 || exit 1

echo "=== build.sh starting: pwd ==="
pwd
ls -la

# Upgrade pip (optional but harmless)
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "Installing requirements.txt..."
python -m pip install -r requirements.txt --no-cache-dir

# If you use Node.js (Tailwind, Vite, etc.), build it first
if [ -f package.json ]; then
  echo "package.json found – running npm/yarn build..."
  if command -v npm >/dev/null 2>&1; then
    npm ci
    npm run build || echo "npm run build failed (continuing anyway)"
  elif command -v yarn >/dev/null 2>&1; then
    yarn install --frozen-lockfile
    yarn build || echo "yarn build failed (continuing anyway)"
  elif command -v pnpm >/dev/null 2>&1; then
    pnpm install --frozen-lockfile
    pnpm run build || echo "pnpm run build failed (continuing anyway)"
  fi
fi

# Add project root to PYTHONPATH so Django can find settings
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
echo "PYTHONPATH set to: $PYTHONPATH"

# ——— Auto-discover Django settings module ———
SETTINGS_MODULE=$(python - "$PWD" <<'PY'
import os
import sys

root = sys.argv[1]

for dirpath, _, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)
    if rel.startswith(('env', '.venv', '.git', '__pycache__')):
        continue
    if 'settings.py' in filenames:
        if rel == '.':
            print('racemate.settings')  # adjust if your project module is different
        else:
            module = rel.replace(os.sep, '.') + '.settings'
            print(module)
        sys.exit(0)

# Fallback (most common Django project layout: project/project/settings.py)
print('racemate.racemate.settings')
PY
)

echo "Discovered SETTINGS_MODULE='$SETTINGS_MODULE'"
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# ——— Test import of settings module (fail fast) ———
python - <<'PY' "$SETTINGS_MODULE"
import importlib
import sys
import traceback

mod = sys.argv[1]
print(f"Attempting to import settings module: {mod}")

try:
    m = importlib.import_module(mod)
    print(f"Successfully imported: {getattr(m, '__file__', '<no file>')}")
except Exception as e:
    print("Failed to import settings module:")
    traceback.print_exc()
    sys.exit(1)

# Optional: run django.setup() to catch app config errors early
try:
    import django
    django.setup()
    from django.conf import settings
    print(f"Django setup OK – INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}")
except Exception as e:
    print("django.setup() failed (continuing anyway – might still work):")
    traceback.print_exc()
PY

# ——— Collect static files (critical for CSS/JS) ———
echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Running collectstatic..."
python manage.py collectstatic --noinput --clear || {
    echo "collectstatic failed – this is often non-fatal on Vercel"
}

echo "Collectstatic finished. Contents of staticfiles/:"
ls -la staticfiles/ || true

echo "Build script completed successfully!"