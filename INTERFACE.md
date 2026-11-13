# INTERFACE.md: navigation map

## Django project (the tutorial blog)
| File | Contents |
|---|---|
| `manage.py` | Django command line (`runserver`, `migrate`, `test blog`) |
| `mysite/settings.py` | settings; `SECRET_KEY` from `DJANGO_SECRET_KEY`, `LOGIN_URL = 'admin:login'` |
| `mysite/settings_demo.py` | web-interface settings: demo database in `.web_demo/` (or `BLOG_DEMO_DB`), `STATIC_URL=/django-static/` |
| `mysite/urls.py` | root URLconf: `admin/` and `include('blog.urls')` |
| `mysite/wsgi.py` | WSGI entry point (deployment) |
| `blog/models.py` | `Post` (author, title, text, created_date, published_date; `publish()`) |
| `blog/views.py` | `published_posts()`, `post_list`, `post_detail`, `post_new`, `post_edit` (login required) |
| `blog/urls.py` | the four blog URL patterns |
| `blog/forms.py` | `PostForm` (title, text) |
| `blog/templates/blog/` | `base.html`, `post_list.html`, `post_detail.html`, `post_edit.html` |
| `blog/static/css/blog.css` | the blog's CSS |
| `blog/migrations/0001_initial.py` | creates the Post table |
| `blog/tests.py` | Django tests for the model and views (`python manage.py test blog`) |

## Web interface (`web/`, port 8256)
| File | Contents |
|---|---|
| `run_web.py` | starts uvicorn on 127.0.0.1:8256 |
| `web/app.py` | FastAPI app: `/api/info`, `/api/posts`, `/api/posts/{pk}`, `/api/anatomy`, `/api/code/tree`, `/api/code/file/{slug}`, `/api/code/search`, `POST /api/try`; mounts Django (ASGI) at `/django/`; `STATIC_ENDPOINTS` |
| `web/django_setup.py` | `setup()`: Django on settings_demo, migrate, seed |
| `web/demo_posts.py` | `COMMITS`, `demo_posts()`, `seed()`: labelled demo posts from the 2017 commits |
| `web/blog_data.py` | `posts()`, `post(pk)`: posts as JSON via `published_posts()` and Django's filters |
| `web/anatomy.py` | `anatomy()`: models, form, `url_patterns()`, views, templates, settings, migrations with file:line |
| `web/code_index.py` | `tree()`, `file(slug)`, `search(q)`, `redact()`, `slug()` for the code explorer |
| `web/static/` | `index.html`, `core.js` + `style.css` (shared kit), `style_app.css`, `main.js`, `static_api.js`, pages `home.js`, `blog.js`, `how.js`, `router.js`, `code.js`, `about.js`; `url_engine.js` (Django resolver port) + `url_engine.test.mjs`; `highlight.js` |
| `scripts/build_static.py` | exports the static site (`site/`) |
| `scripts/make_resolve_fixture.py` | writes `tests/fixtures/resolve_cases.json` and `url_patterns.json` from Django |
| `scripts/screenshots.py` | Playwright smoke test and README images (`docs/img/`) |
| `tests/test_web.py` | API, static build, fixture currency, Django tests, node test |
| `.github/workflows/pages.yml` | Pages build on push to `master` |

Flow: `web/app.py` -> `django_setup.setup()` -> `blog_data` / `anatomy` (import `blog.*`) -> JSON -> `static/*.js` pages.
