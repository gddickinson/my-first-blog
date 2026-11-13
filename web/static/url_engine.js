// Django's URL resolution, ported from django/urls/resolvers.py (Django 5.2) for the patterns this blog defines.
// The patterns come from the API (exported from Django's own resolver), so nothing here is specific to this blog.
// Rules reproduced: the root resolver strips the leading '/'; an include() pattern is searched and the rest of the
// path goes to its children; an endpoint whose regex ends in '$' must match the whole remaining path (fullmatch),
// other endpoints are searched; named groups become kwargs. Python's \d matches any Unicode decimal digit (str
// patterns), so it becomes \p{Nd}. CommonMiddleware's APPEND_SLASH redirect is reproduced by appendSlash().

export function toJsRegex(rx, whole = false) {
  const src = rx.replace(/\(\?P</g, '(?<').replace(/\\d/g, '\\p{Nd}');
  return new RegExp(whole ? `^(?:${src})$` : src, 'u');
}

function matchPattern(p, path) {
  const isEndpoint = !(p.children || p.include);
  const whole = isEndpoint && p.regex.endsWith('$');
  const m = toJsRegex(p.regex, whole).exec(path);
  if (!m) return null;
  const kwargs = {};
  for (const [k, v] of Object.entries(m.groups || {})) if (v !== undefined) kwargs[k] = v;
  return { rest: path.slice(m.index + m[0].length), kwargs };
}

// Resolve a path such as '/post/3/'. Returns { match, view, name, kwargs, namespace, trail } where trail lists every
// pattern tried, in order, with hit true/false (for the page's step-by-step view).
export function resolve(patterns, path) {
  const trail = [];
  if (!path.startsWith('/')) return { match: false, trail };
  const r = walk(patterns, path.slice(1), trail, 0);
  return r ? { ...r, match: true, trail } : { match: false, trail };
}

function walk(patterns, path, trail, depth) {
  for (const p of patterns) {
    const m = matchPattern(p, path);
    trail.push({ regex: p.regex, depth, hit: !!m, tried: path, file: p.file, line: p.line, view: p.view || null,
      include: p.include || null });
    if (!m) continue;
    if (p.namespace) return { view: null, name: null, kwargs: {}, namespace: p.namespace };
    if (p.children) {
      const r = walk(p.children, m.rest, trail, depth + 1);
      if (r) return r;
      continue;
    }
    return { view: p.view, name: p.name, kwargs: m.kwargs, namespace: null };
  }
  return null;
}

// CommonMiddleware (APPEND_SLASH = True): a path that does not resolve, does not end in '/', but resolves with a
// slash added is answered with a 301 redirect to path + '/'.
export function appendSlash(patterns, path) {
  return !!path && !path.endsWith('/') && !resolve(patterns, path).match && resolve(patterns, path + '/').match;
}
