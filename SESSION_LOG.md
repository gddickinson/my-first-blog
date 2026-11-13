# Session log

## 2026-11-13: web interface (web-interface branch)
- Django 1.11 cannot import on Python 3.8+, so the blog was moved to Django 5.2.19 LTS with minimal changes
  (on_delete, re_path, `{% load static %}`, DEFAULT_AUTO_FIELD); added blog/tests.py tests.
- SECRET_KEY moved out of mysite/settings.py into the DJANGO_SECRET_KEY env var (the old key is still in git
  history; George decides whether to purge/rotate).
- Fixed: anonymous visitors could open /post/new/ and a POST crashed with a 500 (now login required, admin login).
- Fixed: base.html closed </body></html> twice.
- Added the web interface (FastAPI shell, port 8256, real Django mounted at /django/, demo DB from the blog's own
  migrations with labelled demo posts), static Pages site (blog read-only, How it works, URL router, code explorer),
  JS port of Django's URL resolver checked against django.urls.resolve on 21 paths.
