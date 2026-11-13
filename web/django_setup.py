"""Start Django inside the FastAPI process, on the demo database (mysite/settings_demo.py).

setup() is idempotent: the first call configures Django, runs the blog's own migrations on the demo
SQLite file and seeds it with the demo posts if it has none.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_ready = False


def setup() -> None:
    global _ready
    if _ready:
        return
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings_demo"  # never the real db.sqlite3
    import django
    from django.conf import settings
    django.setup()
    Path(settings.DATABASES["default"]["NAME"]).parent.mkdir(parents=True, exist_ok=True)
    from django.core.management import call_command
    call_command("migrate", verbosity=0, interactive=False)
    from .demo_posts import seed
    seed()
    _ready = True
