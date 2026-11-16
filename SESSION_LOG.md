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

## 2026-11-16: old SECRET_KEY purged from git history
- The Django SECRET_KEY once committed in mysite/settings.py was replaced by `REDACTED_OLD_SECRET_KEY` in every
  commit (git-filter-repo --replace-text; George's request). Current files unchanged (same tree), same commit count,
  new commit hashes. The key is now read from the DJANGO_SECRET_KEY environment variable.
- Pre-rewrite mirror kept on the FANTOM backup drive (history_rewrite_2026-11-16). Treat the old key as compromised:
  rotate it on any server that used it. Older clones and GitHub's cached views of old commit SHAs may still hold it.
