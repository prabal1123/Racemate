# api/wsgi.py — robust autodiscovery + export `app` for Vercel
import os
import sys
import traceback
from pathlib import Path
import importlib

# -------------------------
# Robust repo-root detection (walk ancestors for manage.py)
# -------------------------
HERE = Path(__file__).resolve()

repo_root = None
# include HERE.parent then all parents
candidates = [HERE.parent] + list(HERE.parents)

for cand in candidates:
    try:
        if (cand / "manage.py").exists():
            repo_root = cand
            break
    except Exception:
        continue

# fallback: prefer two levels up if nothing found
if repo_root is None:
    repo_root = HERE.parents[2] if len(HERE.parents) >= 3 else HERE.parent

ROOT = repo_root
ROOT_STR = str(ROOT)

# Ensure repo root is first on sys.path
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

# Also ensure the inner racemate package directory is available
inner_racemate = ROOT / "racemate"
if inner_racemate.exists() and str(inner_racemate) not in sys.path:
    sys.path.insert(0, str(inner_racemate))

# Debug info (useful in Vercel logs)
try:
    print("DEBUG: repo_root =", ROOT_STR)
    print("DEBUG: sys.path[0] =", sys.path[0])
    print("DEBUG: sys.path[:4] =", sys.path[:4])
    print("DEBUG: repo root files:", sorted(p.name for p in ROOT.iterdir()))
except Exception:
    pass

# -------------------------
# Discover settings modules
# -------------------------
candidates = [
    "racemate.settings",
    "racemate.racemate.settings",
    "settings",
]

discovered = []
for p in ROOT.rglob("settings.py"):
    try:
        rel = p.relative_to(ROOT).with_suffix("")
        full = ".".join(rel.parts)
        discovered.append(full)
        candidates.append(full)
    except Exception:
        continue

print("DEBUG: discovered settings modules:", discovered)
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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", found)
print("DEBUG: Using DJANGO_SETTINGS_MODULE =", found)

# -------------------------
# Create the standard WSGI application object
# -------------------------
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    print("ERROR: exception while initializing Django WSGI application:")
    traceback.print_exc()
    raise

# Export the WSGI callable as `app` for Vercel to use.
app = application
