#!/usr/bin/env bash
set -euo pipefail

echo "=== Django + Vercel Build (Racemate) – FINAL WORKING VERSION ==="
cd /vercel/path0

# Install dependencies
python -m pip install --upgrade pip > /dev/null 2>&1
python -m pip install -r requirements.txt > /dev/null 2>&1

# CRITICAL: Force the project root into Python path + settings
export PYTHONPATH="/vercel/path0"
export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

echo "PYTHONPATH=$PYTHONPATH"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Verify we can import one of your apps (proof it works)
python - <<'PY'
import sys
import accounts  # ← this will fail if path is wrong
import app_admin
print("SUCCESS: Imported local apps (accounts, app_admin)")
PY

# Now run collectstatic the ONLY way that works reliably on Vercel
echo "=== Running collectstatic ==="
python -m django collectstatic --no-input --clear --verbosity=2

# Final verification
count=$(find staticfiles -type f | wc -l)
echo "Collected $count static files into staticfiles/"

if [ "$count" -eq 0 ]; then
  echo "ERROR: No static files collected!"
  exit 1
fi

echo "Build completed successfully – ready for Vercel!"