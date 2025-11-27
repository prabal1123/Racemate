# api/wsgi.py
# Vercel serverless handler for Django WSGI application.
# This file must expose `handler` for Vercel to invoke.

import os
import sys
import traceback

# --- Adjust this if your Django project is in a subfolder (e.g. "proj_DG" or "Racemate")
# If your repo has the Django project at the repo root, leave PROJECT_SUBDIR = "".
PROJECT_SUBDIR = ""  # e.g. "proj_DG" or "" if racemate/ is at repo root

# Ensure project root (and optional subdir) are on sys.path so 'racemate' can be imported.
ROOT = os.path.dirname(os.path.dirname(__file__))  # one level up from api/
if PROJECT_SUBDIR:
    PROJECT_PATH = os.path.join(ROOT, PROJECT_SUBDIR)
else:
    PROJECT_PATH = ROOT

if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Set Django settings module (adjust if your settings module path is different)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "racemate.settings")

# Helpful debug: print sys.path to logs (comment out in production)
print("DEBUG: sys.path[0:5] =", sys.path[0:5])

# Try to import the WSGI application, show full traceback on failure so Vercel log contains the cause.
try:
    # Import the Django WSGI application object from your project package
    from racemate.wsgi import application  # keep this as-is
except Exception:
    print("ERROR: failed to import racemate.wsgi — printing traceback:")
    traceback.print_exc()
    # re-raise so Vercel failure log contains the exception type
    raise

# Create the handler for Vercel.
# Prefer vercel_wsgi if available (add it to requirements). If not installed, raise a clear error.
try:
    # vercel-wsgi provides make_lambda_handler
    from vercel_wsgi import make_lambda_handler
    handler = make_lambda_handler(application)
except Exception as exc:
    # If vercel_wsgi not installed, show a helpful message and re-raise
    print("WARNING: vercel_wsgi not available or failed to initialize. Exception:")
    traceback.print_exc()
    raise RuntimeError(
        "vercel_wsgi is required in production. Add 'vercel-wsgi' to requirements.txt"
    ) from exc
