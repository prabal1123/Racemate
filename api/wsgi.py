from pathlib import Path
import sys
import os

# --- Robust repo-root detection (works locally and on Vercel) ---
# api/wsgi.py is typically at: <repo_root>/api/wsgi.py
HERE = Path(__file__).resolve()
# Candidate 1: parent of api (expected repo root)
CAND1 = HERE.parent.parent        # ../  -> repo root when api/ is at repo_root/api/
# Candidate 2: one level up (handles nested 'racemate' layout)
CAND2 = HERE.parent              # ../api_parent -> sometimes repo root/racemate/api
# Candidate 3: two levels up (safe fallback)
CAND3 = HERE.parents[2] if len(HERE.parents) >= 3 else CAND1

# Choose the candidate that contains manage.py and the top-level racemate folder if possible
repo_root = None
for cand in (CAND1, CAND2, CAND3):
    if (cand / "manage.py").exists() and (cand / "racemate").exists():
        repo_root = cand
        break

# Fallbacks: prefer CAND1, then CAND3, then CAND2
if repo_root is None:
    for cand in (CAND1, CAND3, CAND2):
        if cand.exists():
            repo_root = cand
            break

repo_root = repo_root or CAND1
repo_root_str = str(repo_root)

# Put repository root at the front of sys.path so imports like `import racemate.accounts` work.
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

# Also ensure the inner racemate package directory is available (helps in nested layouts)
inner_racemate = repo_root / "racemate"
if inner_racemate.exists() and str(inner_racemate) not in sys.path:
    sys.path.insert(0, str(inner_racemate))

# DEBUG prints (will show in Vercel logs)
print("DEBUG: repo_root =", repo_root_str)
print("DEBUG: sys.path[0] =", sys.path[0])
print("DEBUG: sys.path[:4] =", sys.path[:4])
print("DEBUG: repo root files:", sorted(p.name for p in repo_root.iterdir()))


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
