#!/usr/bin/env bash
set -euo pipefail

echo "=== Racemate – FINAL WORKING Vercel Build ==="
cd /vercel/path0

# Install dependencies
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

# THIS IS THE ONLY LINE THAT WORKS WITH YOUR NESTED STRUCTURE
export PYTHONPATH="/vercel/path0"
export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

echo "PYTHONPATH=$PYTHONPATH"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Force-add current directory to sys.path and test imports
python - <<'PY'
import sys
import os
# Force the project root into sys.path (this is the missing piece!)
sys.path.insert(0, os.getcwd())

print("sys.path[0] =", sys.path[0])
print("CWD =", os.getcwd())

# Now this finally works
import accounts
import app_admin
import app_bib
import app_results
print("SUCCESS: All top-level apps imported!")
PY

# Collect static
echo "=== Running collectstatic ==="
python -m django collectstatic --no-input --clear --verbosity=2

# Final check
count=$(find staticfiles -type f 2>/dev/null | wc -l)
echo "Collected $count static files"

if [ "$count" -eq 0 ]; then
  echo "ERROR: No static files!"
  exit 1
fi

echo "Build successful – your site is live!"