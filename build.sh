#!/usr/bin/env bash
# build.sh – Vercel Static Build for Django (Racemate)
set -euo pipefail

echo "=== Starting Vercel build ==="
cd /vercel/path0

echo "=== Repository root ==="
pwd
ls -la

echo "=== Searching for settings.py ==="
find . -maxdepth 5 -type f -name "settings.py" -print || true

# --------------------------------------------------
# 1. Upgrade pip & install Python dependencies
# --------------------------------------------------
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# --------------------------------------------------
# 2. Optional: Node.js frontend build (if exists)
# --------------------------------------------------
if [ -f "package.json" ]; then
  echo "=== package.json found – running frontend build ==="
  if command -v npm >/dev/null 2>&1; then
    npm ci --prefer-offline --no-audit
    npm run build || echo "npm run build failed – continuing anyway"
  elif command -v yarn >/dev/null 2>&1; then
    yarn install --frozen-lockfile
    yarn build || echo "yarn build failed – continuing anyway"
  fi
fi

# --------------------------------------------------
# 3. Add project root to PYTHONPATH
# --------------------------------------------------
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
echo "PYTHONPATH=$PYTHONPATH"

# --------------------------------------------------
# 4. Auto-discover Django settings module
# --------------------------------------------------
SETTINGS_MODULE=$(python - "$PWD" <<'PY'
import os, sys
root = sys.argv[1]
for dirpath, _, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)
    if rel.startswith((".git", ".vercel", "env", ".venv", "__pycache__")):
        continue
    if "settings.py" in filenames:
        parts = rel.split(os.sep)
        if parts == ["."]:
            print("settings")
        else:
            print(".".join(parts + ["settings"]))
        sys.exit(0)
# Fallback – your actual project structure
print("racemate.racemate.settings")
PY
)

echo "Discovered SETTINGS_MODULE='$SETTINGS_MODULE'"
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# --------------------------------------------------
# 5. Verify we can import the settings module
# --------------------------------------------------
python - <<PY
import os
import importlib
mod = os.getenv("DJANGO_SETTINGS_MODULE")
print("Testing import of settings module:", mod)
try:
    importlib.import_module(mod)
    print("Settings module imported successfully")
except Exception as e:
    print("Failed to import settings module:", e)
    import traceback; traceback.print_exc()
    exit(1)
PY

# --------------------------------------------------
# 6. Create staticfiles directory and collect static files
# --------------------------------------------------
mkdir -p staticfiles

echo "=== Running collectstatic ==="
DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" \
  python manage.py collectstatic --no-input --clear --verbosity 2

# --------------------------------------------------
# 7. Final verification
# --------------------------------------------------
echo "=== collectstatic completed ==="
echo "Contents of staticfiles/:"
ls -la staticfiles/ | head -20
echo "... (truncated if large)"

FILE_COUNT=$(find staticfiles -type f | wc -l)
echo "Total static files collected: $FILE_COUNT"

if [ "$FILE_COUNT" -eq 0 ]; then
  echo "ERROR: No static files were collected. Check ADMIN or app static configs."
  exit 1
fi

echo "=== Build completed successfully! ==="
echo "Vercel will now serve files from the 'staticfiles' directory."