#!/usr/bin/env bash
set -eux

# Ensure working dir is repo root used by Vercel
cd /vercel/path0

echo "=== pwd ==="
pwd

echo "=== ls -la (repo root) ==="
ls -la

echo "=== find settings.py (maxdepth 4) ==="
find . -maxdepth 4 -type f -name "settings.py" -print || true

# Upgrade pip tooling (optional but helpful)
python -m pip install --upgrade pip setuptools wheel

# Install python deps
python -m pip install -r requirements.txt

# If you use node/tailwind, build it first so collectstatic can pick up the generated CSS.
if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    npm ci
    npm run build
  elif command -v yarn >/dev/null 2>&1; then
    yarn install --frozen-lockfile
    yarn build
  fi
fi

# Add repo root to PYTHONPATH
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
echo "PYTHONPATH set to: $PYTHONPATH"

# Auto-discover settings module path:
SETTINGS_MODULE=$(python - "$PWD" <<'PY'
import os, sys
root = sys.argv[1]
for dirpath, dirnames, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)
    if rel.startswith("env") or rel.startswith(".venv") or rel.startswith(".git"):
        continue
    if "settings.py" in filenames:
        if rel == ".":
            module = "settings"
        else:
            module = rel.replace(os.sep, ".") + ".settings"
        print(module)
        sys.exit(0)
# fallback for your layout
print("racemate.racemate.settings")
PY
)

echo "Discovered SETTINGS_MODULE='$SETTINGS_MODULE'"

# Export DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Quick python import check - will fail early if incorrect
python -c "import importlib, sys; mod=sys.argv[1]; print('Attempting to import', mod); importlib.import_module(mod); print('Import OK:', mod)" "$SETTINGS_MODULE"

# Ensure staticfiles dir exists
mkdir -p staticfiles

# Now collectstatic into STATIC_ROOT (staticfiles/)
python manage.py collectstatic --noinput

echo "Collectstatic finished. Listing staticfiles/"
ls -la staticfiles || true
