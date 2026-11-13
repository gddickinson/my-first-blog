"""Write tests/fixtures/resolve_cases.json (how Django itself resolves a set of paths) and url_patterns.json (the
pattern tree the web API exports), for web/static/url_engine.test.mjs.

For each path: the view and kwargs from django.urls.resolve (or a 404), and whether CommonMiddleware's
APPEND_SLASH would redirect to path + '/'. Run: python scripts/make_resolve_fixture.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FIXTURE = ROOT / "tests" / "fixtures" / "resolve_cases.json"
PATTERNS = ROOT / "tests" / "fixtures" / "url_patterns.json"
PATHS = ["/", "/post/1/", "/post/42/edit/", "/post/new/", "/post/new/edit/", "/post/1", "/post/new",
         "/post/1/edit", "/post/abc/", "/post//", "/post/-1/", "/post/007/", "/post/١٢/", "/posts/",
         "/admin/", "/admin/blog/post/", "/admin", "/about/", "/post/1/edit/extra/", "/post/1/\n", ""]


def cases():
    from web import django_setup
    django_setup.setup()
    from django.urls import Resolver404, is_valid_path, resolve
    out = []
    for path in PATHS:
        case = {"path": path}
        try:
            m = resolve(path) if path else (_ for _ in ()).throw(Resolver404())
            case.update(match=True, view=f"{m.func.__module__}.{m.func.__name__}" if not m.namespace else None,
                        name=m.url_name if not m.namespace else None, kwargs=m.kwargs if not m.namespace else {},
                        namespace=m.namespace or None)
        except Resolver404:
            case.update(match=False, append_slash=bool(path) and not path.endswith("/")
                        and bool(is_valid_path(path + "/")))
        out.append(case)
    return out


def patterns():
    from web import anatomy, django_setup
    django_setup.setup()
    return anatomy.url_patterns()


def main():
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(cases(), indent=1, ensure_ascii=False) + "\n")
    PATTERNS.write_text(json.dumps(patterns(), indent=1) + "\n")
    print(f"wrote {FIXTURE} and {PATTERNS}")


if __name__ == "__main__":
    main()
