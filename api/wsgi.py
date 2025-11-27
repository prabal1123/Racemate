
import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Ensure repo root is on sys.path (one level above api/)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "racemate.settings")

# Create the WSGI application
application = get_wsgi_application()

# Minimal adapter for Vercel (exposes handler)
def handler(event, context):
    """
    Vercel will call this handler. Many Vercel python runtimes
    can invoke WSGI apps directly; this wrapper keeps a stable name.
    """
    return application(event, context)
PY
