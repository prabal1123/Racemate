#!/usr/bin/env bash
set -euo pipefail

echo "=== Racemate Vercel Build – FINAL WORKING VERSION ==="
cd /vercel/path0

# Install deps
python -m pip install --upgrade pip > /dev/null 2>&1
python -m pip install -r requirements.txt > /dev/null 2>&1

# THIS LINE IS THE KEY – must include the project root first
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"

export DJANGO_SETTINGS_MODULE="racemate.racemate.settings"

echo "PYTHONPATH = $PYTHONPATH"
echo "Settings = $DJANGO_SETTINGS_MODULE"

# Test that your top-level apps are importable
python -c "
import sys
print('sys.path[0]:', sys.path[0])
import accounts
import app_admin
import app_bib
import app_results
print('All 4 top-level apps imported successfully!')
" || exit 1

# Run collectstatic the only reliable way on Vercel
echo "=== Running collectstatic ==="
python -m django collectstatic --no-input --clear --verbosity=2

# Final check
count=$(find staticfiles -type f 2>/dev/null | wc -l)
echo "Collected $count static files"
[ "$count" -gt 0 ] && echo "BUILD SUCCESSFUL – deploying now!" || exit 1