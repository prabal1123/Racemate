#!/usr/bin/env bash
set -eux

# Ensure working dir is repo root used by Vercel
cd /vercel/path0 || exit 1

echo "=== build.sh starting: pwd ==="
pwd
ls -la

# Upgrade pip tooling (optional)
python -m pip install --upgrade pip setuptools wheel

# Install python deps
python -m pip install -r requirements.txt

# If you use node/tailwind, build it first so collectstatic can pick up generated CSS
if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    npm ci
    npm run build || true
  elif command -v yarn >/dev/null 2>&1; then
    yarn install --frozen-lockfile
    yarn build || true
  fi
fi

# Add repo root to PYTHONPATH so imports like "racemate.racemate.settings" work
export PYTHONPATH="/vercel/path0:${PYTHONPATH:-}"
echo "PYTHONPATH set to: $PYTHONPATH"

# Auto-discover a settings module by searching for settings.py (limited depth)
SETTINGS_MODULE=$(python - "$PWD" <<PY
import os, sys
root = sys.argv[1]
for dirpath, dirnames, filenames in os.walk(root):
    # don't recurse into typical venv or .git directories
    rel = os.path.relpath(dirpath, root)
    if rel.startswith("env") or rel.startswith(".venv") or rel.startswith(".git"):
        continue
    if "settings.py" in filenames:
        if rel == ".":
            print("settings")
        else:
            # convert path to module path
            mod = rel.replace(os.sep, ".") + ".settings"
            print(mod)
        sys.exit(0)
# fallback
print("racemate.settings")
PY
)

echo "Discovered SETTINGS_MODULE='$SETTINGS_MODULE'"

# Export DJANGO_SETTINGS_MODULE for manage.py
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# quick import test (fails fast and prints a readable message)
python - <<PY
import importlib, sys, traceback
mod = sys.argv[1]
print("Attempting to import", mod)
try:
    m = importlib.import_module(mod)
    print("Imported settings module file:", getattr(m, "__file__", "<no file>"))
    # print raw INSTALLED_APPS if available
    if hasattr(m, "INSTALLED_APPS"):
        print("Raw INSTALLED_APPS (module):", getattr(m, "INSTALLED_APPS"))
    else:
        print("No INSTALLED_APPS attribute in module")
    # try django.setup() to validate app imports
    try:
        import django
        django.setup()
        from django.conf import settings as s
        print("Django setup OK. final INSTALLED_APPS (len):", len(s.INSTALLED_APPS))
    except Exception:
        print("ERROR during django.setup():")
        traceback.print_exc()
except Exception:
    print("Import settings module failed:")
    traceback.print_exc()
    sys.exit(1)
PY "$SETTINGS_MODULE"

# ensure STATIC_ROOT dir
mkdir -p staticfiles

# run collectstatic (may fail if settings broken)
python manage.py collectstatic --noinput || true

echo "Collectstatic finished (listing staticfiles/):"
ls -la staticfiles || true
