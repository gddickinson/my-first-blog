"""Settings for the web interface (run_web.py): the normal settings plus a separate demo database.

The demo database is created by the blog's own migrations and seeded with clearly labelled demo posts
(web/demo_posts.py). It lives in .web_demo/ (git-ignored) unless BLOG_DEMO_DB names another file, so the
real db.sqlite3 is never touched.
"""
import os

from .settings import *  # noqa: F401,F403
from .settings import BASE_DIR, DATABASES

DATABASES['default']['NAME'] = os.environ.get(
    'BLOG_DEMO_DB', os.path.join(BASE_DIR, '.web_demo', 'blog_demo.sqlite3'))

# The FastAPI shell serves its own front end at /static/, so the blog's CSS moves to /django-static/.
STATIC_URL = '/django-static/'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']
