# api/wsgi.py — robust autodiscovery + export `app` for Vercel
import os
import sys
import traceback
from pathlib import Path
import importlib

# Ensure repo root on sys.path (one level above api/)
ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Also add outer racemate folder to sys.path if present (handles nested layouts)
outer_racemate = ROOT / "racemate"
if outer_racemate.exists() and str(outer_racemate) not in sys.path:
    sys.path.insert(0, str(outer_racemate))

# --- DEBUG (optional, useful in Vercel logs) ---
print("DEBUG: api/wsgi.py running. sys.path[0] =", sys.path[0])
print("DEBUG: sys.path[:4] =", sys.path[:4])
print("DEBUG: files at project root:", sorted(p.name for p in ROOT.iterdir()))
# --- end debug ---

# Build candidate settings names
candidates = [
    "racemate.settings",
    "racemate.racemate.settings",
    "settings",
]

discovered = []
for p in ROOT.rglob("settings.py"):
    rel = p.relative_to(ROOT).with_suffix("")
    full = ".".join(rel.parts)
    discovered.append(full)
    candidates.append(full)

print("DEBUG: discovered settings modules:", discovered)
print("DEBUG: candidates initial:", candidates)

# Try to import a candidate settings module
found = None
for mod in candidates:
    try:
        importlib.import_module(mod)
        found = mod
        print("DEBUG: successful import of settings module:", mod)
        break
    except Exception as exc:
        print(f"DEBUG: candidate {mod} rejected: {exc!r}")

# Try trimmed discovered candidates if necessary
if not found:
    for full in discovered:
        parts = full.split(".")
        if len(parts) > 2:
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
        "Unable to locate an importable settings module. Tried: " + ", ".join(candidates + discovered)
    )

# Set the discovered settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", found)
print("DEBUG: Using DJANGO_SETTINGS_MODULE =", found)

# Create the standard WSGI application object
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    print("ERROR: exception while initializing Django WSGI application:")
    traceback.print_exc()
    raise

# Export the WSGI callable as `app` for Vercel to use.
# Also keep `application` (standard) for Django tools.
app = application
