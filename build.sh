#!/usr/bin/env bash
set -euo pipefail

echo "=== Racemate – FINAL WORKING Vercel build ==="
cd /vercel/path0

# Install deps
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

# THIS LINE IS THE ONLY ONE THAT WORKS FOR YOUR STRUCTURE
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

echo "PYTHONPATH=$PYTHONPATH"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Proof that the apps are now visible
python - <<'PY'
import sys, os
print("sys.path[0] =", sys.path[0])
print("Current dir =", os.getcwd())
print("Contents:", os.listdir('.'))

import accounts
import app_admin
import app_bib
import app_results
print("SUCCESS: All four top-level apps imported!")
PY

# Collect static files – the only reliable way on Vercel
echo "=== Running collectstatic ==="
python -m django collectstatic --no-input --clear --verbosity=2

# Final count
count=$(find staticfiles -type f 2>/dev/null | wc -l || echo 0)
echo "Collected $count static files"

if [ "$count" -eq 0 ]; then
  echo "ERROR: No static files collected"
  exit 1
fi

echo "Build completed – your site is going live!"