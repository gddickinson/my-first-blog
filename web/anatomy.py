"""'How this Django app works': facts read from the real code, each with its file and line.

Python files are parsed with ast (line numbers, decorators, template names); the URL patterns, model fields
and form fields come from Django itself after setup, so they are what Django actually runs.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "blog" / "templates" / "blog"
SETTINGS_SHOWN = ["DEBUG", "ALLOWED_HOSTS", "INSTALLED_APPS", "MIDDLEWARE", "ROOT_URLCONF", "TEMPLATES",
                  "DATABASES", "TIME_ZONE", "USE_TZ", "STATIC_URL", "LOGIN_URL", "DEFAULT_AUTO_FIELD"]


def _tree(rel):
    return ast.parse((ROOT / rel).read_text(), filename=rel)


def _call_name(node):
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def models():
    from blog.models import Post
    rel = "blog/models.py"
    cls = next(n for n in _tree(rel).body if isinstance(n, ast.ClassDef) and n.name == "Post")
    lines = {t.id: n.lineno for n in cls.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    fields = []
    for f in Post._meta.get_fields():
        if f.auto_created and not f.concrete:
            continue
        opts = {}
        for k in ("max_length", "null", "blank"):
            v = getattr(f, k, None)
            if v not in (None, False):
                opts[k] = v
        if f.has_default():
            d = f.default
            opts["default"] = f"{d.__module__}.{d.__name__}" if callable(d) else repr(d)
        if f.is_relation:
            opts["to"] = f.related_model._meta.label
            opts["on_delete"] = f.remote_field.on_delete.__name__
        fields.append({"name": f.name, "column": f.column, "type": type(f).__name__, "options": opts,
                       "line": lines.get(f.name), "auto": bool(f.auto_created)})
    methods = [{"name": n.name, "line": n.lineno, "end": n.end_lineno,
                "source": ast.get_source_segment((ROOT / rel).read_text(), n)}
               for n in cls.body if isinstance(n, ast.FunctionDef)]
    return {"file": rel, "name": "Post", "line": cls.lineno, "table": Post._meta.db_table,
            "fields": fields, "methods": methods}


def _url_lines():
    out = {}
    for rel in ("mysite/urls.py", "blog/urls.py"):
        for n in ast.walk(_tree(rel)):
            if isinstance(n, ast.Call) and _call_name(n) == "url" and n.args and isinstance(n.args[0], ast.Constant):
                out[(rel, n.args[0].value)] = n.lineno
    return out


def url_patterns():
    """The resolver tree Django uses (regexes as Django compiled them), for the page and the JS resolver."""
    from django.urls import URLResolver, get_resolver
    lines = _url_lines()

    def walk(patterns, rel):
        out = []
        for p in patterns:
            rx = p.pattern.regex.pattern
            if isinstance(p, URLResolver):
                if p.namespace == "admin":
                    out.append({"regex": rx, "include": "django.contrib.admin", "namespace": "admin",
                                "file": rel, "line": lines.get((rel, rx))})
                else:
                    child = p.urlconf_name if isinstance(p.urlconf_name, str) else p.urlconf_name.__name__
                    crel = child.replace(".", "/") + ".py"
                    out.append({"regex": rx, "include": child, "file": rel, "line": lines.get((rel, rx)),
                                "children": walk(p.url_patterns, crel)})
            else:
                cb = p.callback
                out.append({"regex": rx, "name": p.name, "view": f"{cb.__module__}.{cb.__name__}",
                            "file": rel, "line": lines.get((rel, rx))})
        return out
    return walk(get_resolver().url_patterns, "mysite/urls.py")


def views():
    rel = "blog/views.py"
    src = (ROOT / rel).read_text()
    out = []
    for n in _tree(rel).body:
        if not isinstance(n, ast.FunctionDef):
            continue
        consts = [c.value for c in ast.walk(n) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        calls = {_call_name(c) for c in ast.walk(n) if isinstance(c, ast.Call)}
        queries = sorted({ast.unparse(c) for c in ast.walk(n) if isinstance(c, ast.Call)
                          and "objects" in ast.unparse(c.func)})
        queries = [q for q in queries if not any(q != o and q in o for o in queries)]  # outermost call only
        out.append({
            "name": n.name, "line": n.lineno, "end": n.end_lineno, "docstring": ast.get_docstring(n),
            "decorators": [ast.unparse(d) for d in n.decorator_list],
            "templates": [c for c in consts if c.endswith(".html")],
            "redirects_to": sorted({c.args[0].value for c in ast.walk(n) if isinstance(c, ast.Call)
                                    and _call_name(c) == "redirect" and isinstance(c.args[0], ast.Constant)}),
            "handles_post": "POST" in consts, "uses_form": "PostForm" in calls,
            "queries": queries, "get_object_or_404": "get_object_or_404" in calls,
            "calls": sorted(c for c in calls if c in ("published_posts", "render", "redirect")),
            "source": ast.get_source_segment(src, n),
        })
    return {"file": rel, "functions": out}


TAG = re.compile(r"{%\s*(\w+)([^%]*)%}")
VAR = re.compile(r"{{\s*([^}|]+?)\s*(\|[^}]*)?}}")


def templates():
    out = []
    for path in sorted(TEMPLATES.glob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text()
        tags, vars_, urls, ext, blocks = [], [], [], None, []
        for i, line in enumerate(text.splitlines(), 1):
            for m in TAG.finditer(line):
                name, rest = m.group(1), m.group(2).strip()
                tags.append({"tag": name, "args": rest, "line": i})
                if name == "extends":
                    ext = rest.strip("'\"")
                elif name == "block":
                    blocks.append({"name": rest, "line": i})
                elif name == "url":
                    urls.append({"name": rest.split()[0].strip("'\""), "line": i})
            for m in VAR.finditer(line):
                vars_.append({"expr": m.group(1).strip(), "filters": (m.group(2) or "").strip(), "line": i})
        out.append({"file": rel, "name": path.name, "extends": ext, "blocks": blocks, "tags": tags,
                    "variables": vars_, "url_names": urls, "lines": text.count("\n") + 1})
    return out


def settings_file():
    """Top-level assignments in mysite/settings.py (the file, not the demo overrides). SECRET_KEY's value is never shown."""
    rel = "mysite/settings.py"
    src = (ROOT / rel).read_text()
    out = []
    for n in _tree(rel).body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            name = n.targets[0].id
            if name == "SECRET_KEY":
                out.append({"name": name, "line": n.lineno, "value": "(read from the DJANGO_SECRET_KEY env var)"})
            elif name in SETTINGS_SHOWN:
                out.append({"name": name, "line": n.lineno, "value": ast.get_source_segment(src, n.value)})
    return {"file": rel, "settings": out}


def form():
    from blog.forms import PostForm
    rel = "blog/forms.py"
    cls = next(n for n in _tree(rel).body if isinstance(n, ast.ClassDef))
    return {"file": rel, "name": cls.name, "line": cls.lineno, "model": PostForm._meta.model.__name__,
            "fields": list(PostForm._meta.fields)}


def migrations():
    import importlib
    out = []
    for path in sorted((ROOT / "blog" / "migrations").glob("0*.py")):
        mod = importlib.import_module(f"blog.migrations.{path.stem}")
        head = path.read_text().splitlines()[:3]
        gen = next((h.lstrip("# ") for h in head if h.startswith("# Generated")), None)
        ops = [{"op": type(o).__name__, "model": getattr(o, "name", None),
                "fields": [f for f, _ in getattr(o, "fields", [])]} for o in mod.Migration.operations]
        out.append({"file": path.relative_to(ROOT).as_posix(), "generated": gen, "operations": ops})
    return out


def anatomy():
    return {"model": models(), "form": form(), "urls": url_patterns(), "views": views(),
            "templates": templates(), "settings": settings_file(), "migrations": migrations()}
