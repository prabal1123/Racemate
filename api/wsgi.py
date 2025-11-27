# api/wsgi.py — robust WSGI handler for Vercel (auto-detects package name and sets sys.path)
import os
import sys
import traceback
from pathlib import Path

# Ensure repo root (one level up from api/) is on sys.path
ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Helpful debug — Vercel will capture stdout
print("DEBUG: api/wsgi.py running. sys.path[0] =", sys.path[0])
print("DEBUG: files at project root:", sorted(p.name for p in ROOT.iterdir()))

# Try candidate package names (lowercase and Capitalized)
CANDIDATES = ["racemate", "Racemate"]
found = None
for pkg in CANDIDATES:
    try:
        __import__(pkg)
        found = pkg
        break
    except Exception:
        # ignore import error here — we'll report if none found
        pass

if not found:
    print("ERROR: Could not import any candidate package names:", CANDIDATES)
    print("Make sure your Django project package folder (contains settings.py) is committed to the repo.")
    # Show directory listing for debugging
    try:
        for p in ROOT.iterdir():
            print(" -", p.name)
    except Exception:
        pass
    # Raise to produce an error in logs
    raise ImportError(f"Could not find project package. Expected one of: {CANDIDATES}")

# Use discovered package name for settings
settings_module = f"{found}.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
print(f"DEBUG: Using settings module: {settings_module}")

# Import and create WSGI app
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    print("ERROR: Exception while initializing Django WSGI application:")
    traceback.print_exc()
    raise

# Minimal handler Vercel expects
def handler(event, context):
    # this wrapper exists so Vercel can call `handler`
    return application(event, context)
