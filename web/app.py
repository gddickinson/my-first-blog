"""FastAPI web app for George's Django Girls blog: the JSON API under /api, the front end in static/, and the
real Django blog (ASGI) at /django/ on the demo database.

Run with `python run_web.py` (http://127.0.0.1:8256, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.
"""
import re
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import django_setup

django_setup.setup()

import django  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

from . import anatomy, blog_data, code_index  # noqa: E402
from .demo_posts import COMMITS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="George's Blog (Django Girls)")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
# What `collectstatic` would gather: the blog's CSS and the admin site's files.
app.mount("/django-static", StaticFiles(directory=ROOT / "blog" / "static", packages=[("django.contrib.admin", "static")]),
          name="django-static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/django", include_in_schema=False)
def django_root():
    return RedirectResponse("/django/")


@app.get("/api/info")
def info():
    """Project summary for the home page (all counts from the code and the demo database)."""
    p = blog_data.posts()
    t = code_index.tree()
    a = anatomy.anatomy()
    n_urls = sum(len(u.get("children", [])) or 1 for u in a["urls"])
    return {"title": "George's Blog", "django": django.get_version(),
            "posts": len(p["front_page"]) + len(p["not_on_front_page"]), "published": len(p["front_page"]),
            "views": len(a["views"]["functions"]), "templates": len(a["templates"]), "url_patterns": n_urls,
            "files": len(t["files"]), "lines": t["total_lines"],
            "app_files": sum(f["group"] == "Django app" for f in t["files"]),
            "app_lines": sum(f["lines"] for f in t["files"] if f["group"] == "Django app"),
            "commits_2017": len(COMMITS)}


@app.get("/api/posts")
def posts():
    return blog_data.posts()


@app.get("/api/posts/{pk}")
def post(pk: int):
    p = blog_data.post(pk)
    if p is None:
        raise HTTPException(404, "No such post")
    return p


@app.get("/api/anatomy")
def get_anatomy():
    return anatomy.anatomy()


@app.get("/api/code/tree")
def code_tree():
    return code_index.tree()


@app.get("/api/code/file/{key}")
def code_file(key: str):
    f = code_index.file(key)
    if f is None:
        raise HTTPException(404, "No such file")
    return f


@app.get("/api/code/search")
def code_search(q: str):
    return code_index.search(q)


@app.post("/api/try")
def try_path(body: dict = Body(...)):
    """GET a path from the real Django app (demo database) and report what happened. Local server only."""
    from django.test import Client
    path = str(body.get("path", "/"))
    if not path.startswith("/"):
        path = "/" + path
    from django.urls import Resolver404, resolve
    r = Client().get(path)
    try:
        m = resolve(path)
        view = f"{m.func.__module__}.{m.func.__name__}"
    except Resolver404:
        view = None
    title = re.search(r"<title>(.*?)</title>", r.content.decode(errors="replace"), re.S)
    return {"path": path, "status": r.status_code, "location": r.get("Location"), "view": view,
            "title": title.group(1).strip() if title else None, "bytes": len(r.content)}


app.mount("/django", get_asgi_application(), name="django")

# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = (["/info", "/posts", "/anatomy", "/code/tree"]
                    + [f"/posts/{p['pk']}" for p in blog_data.posts()["front_page"] + blog_data.posts()["not_on_front_page"]]
                    + [f"/code/file/{f['slug']}" for f in code_index.tree()["files"]])
