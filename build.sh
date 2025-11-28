#!/usr/bin/env bash
set -euo pipefail

echo "=== Racemate – FINAL WORKING BUILD ==="
cd /vercel/path0

python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

export PYTHONPATH="/vercel/path0"
export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

python - <<'PY'
import sys, os
sys.path.insert(0, os.getcwd())
import accounts, app_admin, app_bib, app_results
print("All apps imported successfully!")
PY

echo "=== Running collectstatic ==="
python -m django collectstatic --no-input --clear

count=$(find staticfiles -type f | wc -l)
echo "Collected $count static files"
[ "$count" -gt 0 ] || exit 1

echo "Deploying now – your site is live!"