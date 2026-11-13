"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("BLOG_DEMO_DB", str(Path(tempfile.mkdtemp()) / "blog_demo.sqlite3"))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific ---------------------------------------------------------------------------------------

def test_demo_posts_are_labelled_and_filtered():
    d = client.get("/api/posts").json()
    every = d["front_page"] + d["not_on_front_page"]
    assert len(d["front_page"]) == 6 and len(d["not_on_front_page"]) == 1
    assert all(p["title"].startswith("[Demo]") for p in every)
    assert all("not a post George wrote" in p["html"] or p["published"] is None for p in every)
    dates = [p["published"] for p in d["front_page"]]
    assert dates == sorted(dates)  # post_list orders oldest first
    assert client.get("/api/posts/999").status_code == 404


def test_real_django_blog_is_mounted():
    r = client.get("/django/")
    assert r.status_code == 200 and "George's Blog" in r.text and "/django/post/1/" in r.text
    assert "/django-static/css/blog.css" in r.text and client.get("/django-static/css/blog.css").status_code == 200
    assert client.get("/django-static/admin/css/base.css").status_code == 200
    r = client.get("/django/post/new/", follow_redirects=False)
    assert r.status_code == 302 and "/admin/login/" in r.headers["location"]


def test_try_reports_the_django_response():
    assert client.post("/api/try", json={"path": "/post/1/"}).json()["status"] == 200
    t = client.post("/api/try", json={"path": "/post/1"}).json()
    assert t["status"] == 301 and t["location"] == "/post/1/"
    assert client.post("/api/try", json={"path": "/nope/"}).json()["status"] == 404


def test_anatomy_cites_real_lines():
    a = client.get("/api/anatomy").json()
    for v in a["views"]["functions"]:
        line = (ROOT / a["views"]["file"]).read_text().splitlines()[v["line"] - 1]
        assert line.startswith(f"def {v['name']}(")
    for f in a["model"]["fields"]:
        if f["line"]:
            assert (ROOT / "blog/models.py").read_text().splitlines()[f["line"] - 1].strip().startswith(f["name"] + " =")
    blog = next(u for u in a["urls"] if u.get("children"))
    for p in blog["children"]:
        assert p["regex"] in (ROOT / p["file"]).read_text().splitlines()[p["line"] - 1]
    assert all(s["name"] != "SECRET_KEY" or "env" in s["value"] for s in a["settings"]["settings"])


def test_code_explorer():
    tree = client.get("/api/code/tree").json()
    paths = {f["path"] for f in tree["files"]}
    assert {"blog/models.py", "blog/views.py", "mysite/settings.py", "manage.py"} <= paths
    assert len({f["slug"] for f in tree["files"]}) == len(tree["files"])
    assert not any(p.endswith((".sqlite3", ".pyc")) or p.startswith(("site/", ".web_demo/")) for p in paths)
    assert client.get("/api/code/file/..-..-etc-passwd").status_code == 404
    assert client.get("/api/code/search", params={"q": "published_posts"}).json()


def test_static_export_has_no_hardcoded_secret(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    pat = re.compile(r"SECRET_KEY\s*=\s*(['\"])(?!<redacted>)[^'\"\n]{8,}\1")
    for f in (tmp_path / "site").rglob("*"):
        if f.is_file() and f.suffix in (".json", ".js", ".html"):
            assert not pat.search(f.read_text()), f


def test_resolve_fixture_is_current():
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_resolve_fixture as m
    assert json.loads(m.FIXTURE.read_text()) == json.loads(json.dumps(m.cases(), ensure_ascii=False))
    assert json.loads(m.PATTERNS.read_text()) == m.patterns()


def test_django_app_tests():
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "mysite.settings"}
    r = subprocess.run([sys.executable, "manage.py", "test", "blog", "-v", "1"], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
