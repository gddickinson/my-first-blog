// URL router: Django's resolver (url_engine.js) run in the browser on the patterns exported from Django itself.
// On the local app, "Ask Django" also GETs the path from the real blog and reports the response.
import { api, app, esc, go, isStatic, list, needsServer, route } from './core.js';
import { appendSlash, resolve } from './url_engine.js';

const EXAMPLES = ['/', '/post/1/', '/post/7/', '/post/new/', '/post/2/edit/', '/post/1', '/post/abc/', '/admin/', '/about/'];

function verdict(a, r, path) {
  if (r.match && r.namespace) return `<p class="ok"><b>Matched</b> the <code>${esc(r.namespace)}</code> include: Django's
    admin site takes over from here (its own URL patterns are not expanded on this page).</p>`;
  if (r.match) {
    const v = a.views.functions.find(f => r.view.endsWith('.' + f.name));
    const kw = Object.keys(r.kwargs).length ? `with kwargs <code>${esc(JSON.stringify(r.kwargs))}</code>` : 'with no kwargs';
    return `<p class="ok"><b>Matched</b> <code>${esc(r.name)}</code>: Django calls <code>${esc(r.view)}(request${
      Object.keys(r.kwargs).map(k => `, ${esc(k)}=${esc(JSON.stringify(r.kwargs[k]))}`).join('')})</code> ${kw}.</p>
    ${v ? `<p>That view is <a href="#/code/blog-views-py?line=${v.line}">blog/views.py:${v.line}</a>${
      v.decorators.length ? `, decorated with <code>${esc(v.decorators.join(', '))}</code> (anonymous visitors are redirected to the admin login)` : ''}${
      v.templates.length ? `, and renders <code>${esc(v.templates.join(', '))}</code>` : ''}${
      v.get_object_or_404 ? '; a pk with no post gives 404' : ''}.</p>` : ''}`;
  }
  if (appendSlash(a.urls, path)) return `<p class="err"><b>No match</b>, but <code>${esc(path)}/</code> does: Django's
    CommonMiddleware (APPEND_SLASH) answers with a 301 redirect to it.</p>`;
  return `<p class="err"><b>No match</b>: Django answers 404 (with DEBUG = True it lists the patterns it tried, as below).</p>`;
}

function trail(r) {
  return `<ol class="trail">${list(r.trail, t => `<li class="${t.hit ? 'hit' : 'miss'}" style="margin-left:${t.depth * 22}px">
    ${t.hit ? '&#10003;' : '&times;'} <code>${esc(t.regex || "''")}</code> on <code>${esc(JSON.stringify(t.tried))}</code>
    ${t.include ? `&rarr; include(${esc(t.include)})` : t.view ? `&rarr; ${esc(t.view)}` : ''}
    <span class="cite">${t.file ? `<a href="#/code/${t.file.replace(/[^A-Za-z0-9]+/g, '-')}?line=${t.line}">${esc(t.file)}:${t.line}</a>` : ''}</span></li>`)}</ol>`;
}

route('router', async (args, query) => {
  const a = await api('/anatomy');
  const path = query.path ?? '/post/1/';
  app().innerHTML = `
  <p class="kicker">django.urls</p><h1>URL router</h1>
  <p class="lead">How Django picks the view for a path: it strips the leading <code>/</code>, then tries each pattern of
    <code>mysite/urls.py</code> in order; <code>include()</code> hands the rest of the path to <code>blog/urls.py</code>.
    This page runs a JavaScript port of Django's resolver on the patterns exported from Django; the tests check it
    agrees with <code>django.urls.resolve</code>.</p>
  <form id="f" class="row"><div><label for="p">Path</label><input id="p" value="${esc(path)}" autocomplete="off"></div>
    <div style="flex:0"><button type="submit">Resolve</button></div></form>
  <div class="chips" aria-label="Examples">${list(EXAMPLES, e => `<button type="button" class="alt" data-p="${esc(e)}">${esc(e)}</button>`)}</div>
  <div id="out" class="panel"></div>
  <div id="live" class="panel"></div>`;
  const out = app().querySelector('#out'), live = app().querySelector('#live');
  const r = resolve(a.urls, path);
  out.innerHTML = verdict(a, r, path) + '<h3>Patterns tried</h3>' + trail(r);
  live.innerHTML = isStatic()
    ? `<h3>The real Django response</h3>${needsServer('Asking the running Django app')}`
    : `<h3>The real Django response</h3><button type="button" id="ask">Ask Django</button><div id="ans"></div>`;
  app().querySelector('#f').addEventListener('submit', e => {
    e.preventDefault(); go('#/router?keep=1&path=' + encodeURIComponent(app().querySelector('#p').value));
  });
  app().querySelectorAll('[data-p]').forEach(b => b.addEventListener('click', () => go('#/router?keep=1&path=' + encodeURIComponent(b.dataset.p))));
  const ask = app().querySelector('#ask');
  if (ask) ask.addEventListener('click', async () => {
    const ans = app().querySelector('#ans');
    try {
      const t = await api('/try', { body: { path } });
      ans.innerHTML = `<dl class="kv"><dt>status</dt><dd>${t.status}</dd>${t.location ? `<dt>Location</dt><dd>${esc(t.location)}</dd>` : ''}
        <dt>view</dt><dd>${esc(t.view ?? 'none')}</dd><dt>page title</dt><dd>${esc(t.title ?? '-')}</dd><dt>bytes</dt><dd>${t.bytes}</dd></dl>
        ${t.status === 200 ? `<a href="django${esc(t.path)}">open it</a>` : ''}`;
    } catch (e) { ans.innerHTML = `<p class="err">${esc(e.message)}</p>`; }
  });
});
