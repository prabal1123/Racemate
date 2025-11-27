# api/wsgi.py — add outer racemate folder to sys.path so app imports like "accounts" work
import os
import sys
import traceback
from pathlib import Path
import importlib

# Put repo root on sys.path (one level above api/)
ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Also add the outer 'racemate' directory (if it exists) to sys.path.
# This handles the nested layout: repo-root/racemate/<app folders and inner racemate package>.
outer_racemate = ROOT / "racemate"
if outer_racemate.exists() and str(outer_racemate) not in sys.path:
    sys.path.insert(0, str(outer_racemate))

print("DEBUG: api/wsgi.py running. sys.path[0] =", sys.path[0])
print("DEBUG: sys.path[:4] =", sys.path[:4])
print("DEBUG: files at project root:", sorted(p.name for p in ROOT.iterdir()))
print("DEBUG: outer_racemate on sys.path:", str(outer_racemate) in sys.path)

# Find settings.py modules
candidates = []
for p in ROOT.rglob("settings.py"):
    parts = str(p).split(os.sep)
    if any(x in parts for x in ("env", ".venv", "_vendor", "api", "__pycache__")):
        continue
    rel = p.relative_to(ROOT).with_suffix("")  # e.g. racemate/racemate/settings
    module_path = ".".join(rel.parts)
    candidates.append(module_path)

print("DEBUG: discovered candidate settings modules:", candidates)

found_settings = None
for module_path in candidates:
    try:
        importlib.import_module(module_path)
        found_settings = module_path
        print("DEBUG: successful import of settings module:", module_path)
        break
    except Exception as exc:
        print(f"DEBUG: candidate {module_path} rejected: {exc!r}")

if not found_settings:
    raise ImportError(
        "Unable to locate an importable settings module. Searched: " + ", ".join(candidates)
    )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", found_settings)
print("DEBUG: Using DJANGO_SETTINGS_MODULE =", found_settings)

# Initialize WSGI app
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    print("ERROR: exception while initializing Django WSGI application:")
    traceback.print_exc()
    raise

def handler(event, context):
    return application(event, context)
