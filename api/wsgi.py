# api/wsgi.py — robust final autodetect for Vercel (handles nested racemate/racemate layouts)
import os
import sys
import traceback
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Also add outer 'racemate' folder (if exists) so top-level app imports work
outer_racemate = ROOT / "racemate"
if outer_racemate.exists() and str(outer_racemate) not in sys.path:
    sys.path.insert(0, str(outer_racemate))

print("DEBUG: api/wsgi.py running. sys.path[0] =", sys.path[0])
print("DEBUG: sys.path[:4] =", sys.path[:4])
print("DEBUG: files at project root:", sorted(p.name for p in ROOT.iterdir()))
print("DEBUG: outer_racemate on sys.path:", str(outer_racemate) in sys.path)

# Build a list of candidate settings module names to try, in priority order.
# 1) Typical when sys.path[0] is repo root and package is racemate/: "racemate.settings"
# 2) If nested racemate/racemate exists and sys.path[0] is repo root: "racemate.racemate.settings"
# 3) If sys.path[0] is inner racemate, "racemate.settings" will succeed
# 4) Try discovered file-based modules adjusted for current sys.path
candidates = [
    "racemate.settings",
    "racemate.racemate.settings",
    "settings",
]

# Add discovered settings.py paths (converted to module paths)
discovered = []
for p in ROOT.rglob("settings.py"):
    parts = p.relative_to(ROOT).with_suffix("").parts  # e.g. ('racemate','racemate','settings')
    full = ".".join(parts)
    discovered.append(full)
    # also try trimmed imports by removing leading folder if sys.path[0] is inside that folder
    # e.g. if full == "racemate.racemate.settings" and sys.path[0] endswith "/racemate",
    # try "racemate.settings"
    candidates.append(full)

print("DEBUG: discovered settings modules from files:", discovered)
print("DEBUG: candidates initial:", candidates)

found = None
for mod in candidates:
    try:
        importlib.import_module(mod)
        found = mod
        print("DEBUG: successful import of settings module:", mod)
        break
    except Exception as exc:
        print(f"DEBUG: candidate {mod} rejected: {exc!r}")

# Final attempt: try trimming the first segment of discovered modules (handle inner-folder sys.path)
if not found:
    for full in discovered:
        parts = full.split(".")
        if len(parts) > 2:
            # try removing the first segment (e.g. "racemate.racemate.settings" -> "racemate.settings")
            trimmed = ".".join(parts[1:])
            try:
                importlib.import_module(trimmed)
                found = trimmed
                print("DEBUG: successful import of trimmed settings module:", trimmed)
                break
            except Exception as exc:
                print(f"DEBUG: trimmed candidate {trimmed} rejected: {exc!r}")

if not found:
    raise ImportError(
        "Unable to locate an importable settings module. Tried candidates: "
        + ", ".join(candidates + discovered)
    )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", found)
print("DEBUG: Using DJANGO_SETTINGS_MODULE =", found)

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    print("ERROR: exception while initializing Django WSGI application:")
    traceback.print_exc()
    raise

def handler(event, context):
    return application(event, context)
