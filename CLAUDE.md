# my-first-blog

Django Girls tutorial blog (2017), moved to Django 5.2, plus a web interface (`web/`, port 8256) and GitHub Pages site.

@INTERFACE.md

- Tests: `python -m pytest -q tests` (includes `python manage.py test blog`) and `node web/static/url_engine.test.mjs`.
- The web interface never touches `db.sqlite3`: it uses `mysite/settings_demo.py` (demo DB in `.web_demo/`).
- After changing a `urls.py`, run `python scripts/make_resolve_fixture.py`.
- Never commit a real `SECRET_KEY`; it comes from `DJANGO_SECRET_KEY`.
