# api/wsgi.py — autodetect settings module (handles nested package structures)
import os
import sys
import traceback
from pathlib import Path
import importlib

# Ensure repo root (one level above api/) is on sys.path
ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

print("DEBUG: api/wsgi.py running. sys.path[0] =", sys.path[0])
print("DEBUG: files at project root:", sorted(p.name for p in ROOT.iterdir()))

# Find all settings.py files under the repo root (skip venv, .git, __pycache__, _vendor, api)
candidates = []
for p in ROOT.rglob("settings.py"):
    # ignore settings in env/ or .venv or _vendor or api
    parts = str(p).split(os.sep)
    if any(x in parts for x in ("env", ".venv", "_vendor", "api", "__pycache__")):
        continue
    # build module path from relative path: e.g. racemate/racemate/settings.py -> racemate.racemate.settings
    rel = p.relative_to(ROOT).with_suffix("")  # e.g. racemate/racemate/settings
    module_path = ".".join(rel.parts)
    candidates.append(module_path)

print("DEBUG: discovered candidate settings modules:", candidates)

found_settings = None
for module_path in candidates:
    try:
        importlib.import_module(module_path)
        # ensure it's actually a module we can import (it might import but fail later)
        found_settings = module_path
        print("DEBUG: successful import of settings module:", module_path)
        break
    except Exception as exc:
        print(f"DEBUG: candidate {module_path} rejected: {exc!r}")

if not found_settings:
    raise ImportError(
        "Unable to locate an importable settings module. "
        "Searched these candidates: " + ", ".join(candidates)
    )

# Set the discovered settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", found_settings)
print("DEBUG: Using DJANGO_SETTINGS_MODULE =", found_settings)

# Create WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    print("ERROR: exception while initializing Django WSGI application:")
    traceback.print_exc()
    raise

# Expose handler expected by Vercel
def handler(event, context):
    return application(event, context)
