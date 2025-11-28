#!/usr/bin/env bash
set -eux

# -----------------------------------------
# 0. Go to Vercel project root
# -----------------------------------------
cd /vercel/path0

echo "=== pwd ==="
pwd
echo "=== ls (repo root) ==="
ls -la

echo "=== Searching for settings.py ==="
find . -maxdepth 4 -type f -name "settings.py" -print || true

# -----------------------------------------
# 1. Upgrade pip tooling
# -----------------------------------------
python -m pip install --upgrade pip setuptools wheel

# -----------------------------------------
# 2. Install python dependencies
# -----------------------------------------
python -m pip install -r requirements.txt

# -----------------------------------------
# 3. Node build (if present)
# -----------------------------------------
if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    npm ci
    npm run build
  elif command -v yarn >/dev/null 2>&1; then
    yarn install --frozen-lockfile
    yarn build
  fi
fi

# -----------------------------------------
# 4. Add repo root to PYTHONPATH
# -----------------------------------------
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
echo "PYTHONPATH set to: $PYTHONPATH"

# -----------------------------------------
# 5. Auto-discover Django settings module
# -----------------------------------------
SETTINGS_MODULE=$(python - "$PWD" <<'PY'
import os, sys
root = sys.argv[1]

for dirpath, _, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)

    # Skip venv
    if rel.startswith(("env", ".venv", ".git")):
        continue

    if "settings.py" in filenames:
        if rel == ".":
            print("settings")
        else:
            print(rel.replace(os.sep, ".") + ".settings")
        sys.exit(0)

# fallback (your project)
print("racemate.racemate.settings")
PY
)

echo "Discovered SETTINGS_MODULE='$SETTINGS_MODULE'"

export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# -----------------------------------------
# 6. Python import check
# -----------------------------------------
python - <<PY
import importlib, sys
mod = "${SETTINGS_MODULE}"
print("Import test:", mod)
importlib.import_module(mod)
print("Import OK:", mod)
PY

# -----------------------------------------
# 7. Run collectstatic (debug wrapped)
# -----------------------------------------
mkdir -p staticfiles

echo "=== Running collectstatic (debug mode) ==="
python - <<'PY' || true
import traceback, os
from django.core import management

try:
    management.call_command("collectstatic", verbosity=2, interactive=False)
except Exception:
    print("\n=== Collectstatic ERROR ===")
    traceback.print_exc()

    # Save traceback to Vercel output folder
    os.makedirs("/vercel/output", exist_ok=True)
    with open("/vercel/output/collectstatic-error.txt", "w") as f:
        traceback.print_exc(file=f)

    raise
PY

echo "=== collectstatic completed ==="
ls -la staticfiles || true
