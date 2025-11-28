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

echo "=== DEBUG: show Django settings + INSTALLED_APPS ==="
python - <<'PY'
import importlib, sys, traceback
mod = "${SETTINGS_MODULE}"
print("DJANGO_SETTINGS_MODULE:", mod)
try:
    settings = importlib.import_module(mod)
    # If django is already configured, use django.conf.settings; otherwise import and run setup
    import django
    from django.conf import settings as djsettings
    print("settings module file:", getattr(settings, '__file__', '<no __file__>'))
    # Print raw INSTALLED_APPS from module (before Django app registry)
    print("\nraw installed apps from module (settings.INSTALLED_APPS):")
    try:
        print(settings.INSTALLED_APPS)
    except Exception as e:
        print("Could not read INSTALLED_APPS from module:", e)
    # Now try to configure Django and print app registry import results
    try:
        django.setup()
        from django.conf import settings as s
        print("\nDjango setup completed. settings module path (django):", getattr(s, '__file__', '<no __file>'))
        print("\nFinal INSTALLED_APPS (django.conf.settings.INSTALLED_APPS):")
        print(list(s.INSTALLED_APPS))
    except Exception as e:
        print("\nERROR during django.setup():")
        traceback.print_exc()
        # Try to show partial app import errors:
        try:
            from django.apps import apps
            print("\nRegistered app configs:", [a.name for a in apps.get_app_configs()])
        except Exception:
            print("apps.get_app_configs() also failed")
            traceback.print_exc()
except Exception:
    print("Import settings module failed:")
    traceback.print_exc()
PY

echo "=== collectstatic completed ==="
ls -la staticfiles || true
