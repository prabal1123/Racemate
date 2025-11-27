# api/wsgi.py — minimal, canonical WSGI application for Vercel
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path (one level above api/)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# If you have an outer directory with apps (repo_root/racemate/*), add that too
outer_racemate = ROOT / "racemate"
if outer_racemate.exists() and str(outer_racemate) not in sys.path:
    sys.path.insert(0, str(outer_racemate))

# Discover settings module: try common names, falling back to file scan
candidates = [
    "racemate.settings",
    "racemate.racemate.settings",
    "settings",
]

# Add discovered file-based candidates
from pathlib import Path as _P
for p in ROOT.rglob("settings.py"):
    rel = p.relative_to(ROOT).with_suffix("")
    candidates.append(".".join(rel.parts))

# Set first importable candidate
import importlib
chosen = None
for cand in candidates:
    try:
        importlib.import_module(cand)
        chosen = cand
        break
    except Exception:
        continue

if chosen is None:
    raise ImportError("Could not determine DJANGO_SETTINGS_MODULE from candidates: " + ", ".join(candidates))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", chosen)

# Create the standard WSGI application object
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Do NOT export any other objects named 'handler' or similar — leave only 'application'
