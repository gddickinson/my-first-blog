// "How this Django app works": every fact comes from /api/anatomy (web/anatomy.py reads the real code and asks
// Django), and every claim links to its file and line in the code explorer.
import { api, app, esc, list, route } from './core.js';
import { highlightLines } from './highlight.js';

const slug = f => f.replace(/[^A-Za-z0-9]+/g, '-');
const cite = (file, line) => `<a class="cite" href="#/code/${slug(file)}${line ? `?line=${line}` : ''}">${esc(file)}${line ? ':' + line : ''}</a>`;
const code = (src, lang = 'python') => `<pre>${highlightLines(src, lang).join('\n')}</pre>`;
// line of the first statement containing `needle` inside a view, as a file line number
const lineOf = (v, needle) => { const i = v.source.split('\n').findIndex(l => l.includes(needle)); return i < 0 ? null : v.line + i; };

function flowSvg(a) {
  const blogUrls = a.urls.find(u => u.children);
  const boxes = [
    ['Browser', 'GET /post/3/', null],
    ['mysite/urls.py', `${a.urls.length} patterns; include()`, blogUrls],
    ['blog/urls.py', `${blogUrls.children.length} patterns`, blogUrls.children[0]],
    ['blog/views.py', 'post_detail(request, pk)', { file: a.views.file, line: a.views.functions.find(f => f.name === 'post_detail')?.line }],
    ['blog/models.py', 'Post (ORM -> SQLite)', { file: a.model.file, line: a.model.line }],
    ['templates', 'post_detail.html + base.html', null],
  ];
  const W = 270, H = 64, gx = 45, gy = 60;
  const pos = boxes.map((_, i) => { const r = Math.floor(i / 3), c = r ? 2 - (i % 3) : i % 3; return [20 + c * (W + gx), 20 + r * (H + gy)]; });
  const rect = (b, [x, y], i) => `<g><rect x="${x}" y="${y}" width="${W}" height="${H}" rx="8" fill="rgba(17,24,49,.95)"
    stroke="${['#ffa53d', '#ff5fa2', '#4fd1a5'][i % 3]}" stroke-width="1.5"/>
    <text x="${x + 14}" y="${y + 26}">${esc(b[0])}</text><text class="sub" x="${x + 14}" y="${y + 47}">${esc(b[1])}</text></g>`;
  const arrow = (i) => {
    const [x1, y1] = pos[i], [x2, y2] = pos[i + 1];
    if (y1 === y2) { const l = x2 > x1; const sx = l ? x1 + W : x1, ex = l ? x2 : x2 + W;
      return `<line x1="${sx}" y1="${y1 + H / 2}" x2="${ex + (l ? -6 : 6)}" y2="${y2 + H / 2}" stroke="#94a3c6" stroke-width="2" marker-end="url(#ah)"/>`; }
    return `<line x1="${x1 + W / 2}" y1="${y1 + H}" x2="${x2 + W / 2}" y2="${y2 - 6}" stroke="#94a3c6" stroke-width="2" marker-end="url(#ah)"/>`;
  };
  const back = `<path d="M ${pos[5][0]} ${pos[5][1] + H / 2} C -10 ${pos[5][1] + H / 2}, -10 ${pos[0][1] + H}, ${pos[0][0] + 40} ${pos[0][1] + H + 4}"
    fill="none" stroke="#ffa53d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ah2)"/>
    <text class="sub" x="${pos[5][0] - 4}" y="${pos[5][1] + H + 22}">HTML response back to the browser</text>`;
  return `<svg viewBox="0 0 ${3 * W + 2 * gx + 40} ${2 * H + gy + 60}" role="img" aria-label="Request flow: browser, mysite/urls.py, blog/urls.py, blog/views.py, blog/models.py, templates, response">
    <defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#94a3c6"/></marker>
    <marker id="ah2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ffa53d"/></marker></defs>
    ${boxes.map((b, i) => rect(b, pos[i], i)).join('')}${boxes.slice(0, -1).map((_, i) => arrow(i)).join('')}${back}</svg>`;
}

function viewsTable(a) {
  const blog = a.urls.find(u => u.children).children;
  return `<div class="scroll"><table><thead><tr><th>View</th><th>URL pattern</th><th>Login</th><th>Model access</th><th>Template / result</th></tr></thead><tbody>
    ${list(a.views.functions, v => {
      const u = blog.find(p => p.view.endsWith('.' + v.name));
      return `<tr><td><code>${esc(v.name)}</code><br>${cite(a.views.file, v.line)}</td>
        <td>${u ? `<code>${esc(u.regex)}</code><br>${cite(u.file, u.line)}` : '<span class="mute">helper, no URL</span>'}</td>
        <td>${v.decorators.length ? esc(v.decorators.join(', ')) : '-'}</td>
        <td class="mono small">${v.queries.length ? list(v.queries, q => esc(q), '<br>') : v.get_object_or_404 ? 'get_object_or_404(Post, pk=pk)' : v.calls.includes('published_posts') ? 'published_posts()' : '-'}</td>
        <td class="small">${list(v.templates, t => `<code>${esc(t)}</code>`, ', ')}${v.redirects_to.length ? `<br>POST: redirect to <code>${esc(v.redirects_to.join(', '))}</code>` : ''}</td></tr>`;
    })}</tbody></table></div>`;
}

function writeFlow(a) {
  const v = a.views.functions.find(f => f.name === 'post_new');
  if (!v) return '';
  const steps = [
    ['@login_required', 'anonymous visitors are sent to LOGIN_URL (the admin login)'],
    ['if request.method == "POST"', 'a GET shows an empty PostForm; a POST carries the filled-in form'],
    ['form.is_valid()', 'PostForm checks title (max 200 characters) and text'],
    ['form.save(commit=False)', 'builds a Post without saving it yet'],
    ['post.author = request.user', 'the logged-in user becomes the author'],
    ['post.published_date = timezone.now()', 'published straight away, so it appears on the front page'],
    ['redirect(', "then the browser is sent to the new post's page", "redirect('post_detail', pk=post.pk)"],
  ];
  return `<ol>${list(steps, ([needle, what, label]) => { const ln = lineOf(v, needle);
    return ln ? `<li><code>${esc(label || needle)}</code>: ${esc(what)} ${cite(a.views.file, ln)}</li>` : ''; })}</ol>
    <details><summary class="small">Source of post_new</summary>${code(v.source)}</details>`;
}

function templatesBlock(a) {
  return `<div class="grid wide">${list(a.templates, t => `<div class="card"><b>${esc(t.name)}</b><small>${cite(t.file)} · ${t.lines} lines</small>
    <span>${t.extends ? `extends <code>${esc(t.extends)}</code>` : 'the page skeleton (no extends)'}${t.blocks.length ? `; block <code>${esc(t.blocks.map(b => b.name).join(', '))}</code>` : ''}</span>
    <span class="small">tags: ${esc([...new Set(t.tags.map(x => x.tag))].join(', ') || 'none')}</span>
    <span class="small">variables: ${list(t.variables, x => `<code>${esc(x.expr + (x.filters ? ' ' + x.filters : ''))}</code>`, ', ') || 'none'}</span>
    ${t.url_names.length ? `<span class="small">links to: ${list(t.url_names, x => `<code>${esc(x.name)}</code>`, ', ')}</span>` : ''}</div>`)}</div>`;
}

route('how', async () => {
  const a = await api('/anatomy');
  const m = a.model;
  app().innerHTML = `
  <p class="kicker">From the real code</p><h1>How this Django app works</h1>
  <p class="lead">One project (<code>mysite</code>) holding one app (<code>blog</code>). Everything on this page is
    read from the code by <code>web/anatomy.py</code> or asked of Django itself; each link opens the line in the code explorer.</p>
  <div class="panel flow">${flowSvg(a)}</div>
  <h2>1. URLs pick a view</h2>
  <p>Django starts at <code>ROOT_URLCONF</code> (${cite('mysite/settings.py', a.settings.settings.find(s => s.name === 'ROOT_URLCONF')?.line)}).
    <code>mysite/urls.py</code> sends <code>admin/</code> to Django's admin site and everything else to
    <code>blog/urls.py</code> with <code>include()</code>. <a href="#/router">Try it in the URL router.</a></p>
  ${viewsTable(a)}
  <h2>2. The model is the database table</h2>
  <p><code>Post</code> (${cite(m.file, m.line)}) is stored in the table <code>${esc(m.table)}</code>.
    ${a.migrations.map(g => `${cite(g.file)} (${esc(g.generated || 'migration')}) creates it with ${g.operations.map(o => `${esc(o.op)} ${esc(o.model)}`).join(', ')}.`).join(' ')}</p>
  <div class="scroll"><table><thead><tr><th>Field</th><th>Type</th><th>Options</th><th>Line</th></tr></thead><tbody>
    ${list(m.fields, f => `<tr><td><code>${esc(f.name)}</code>${f.column !== f.name ? ` <span class="mute small">(column ${esc(f.column)})</span>` : ''}</td>
      <td>${esc(f.type)}</td><td class="mono small">${esc(Object.entries(f.options).map(([k, v]) => `${k}=${v}`).join(', ') || '-')}</td>
      <td>${f.auto ? '<span class="mute small">added by Django</span>' : cite(m.file, f.line)}</td></tr>`)}</tbody></table></div>
  <div class="two">${list(m.methods, x => `<div><h3>${esc(x.name)}() ${cite(m.file, x.line)}</h3>${code(x.source)}</div>`)}</div>
  <h2>3. Views ask the model and render a template</h2>
  <p>The front page calls <code>published_posts()</code>, which filters on <code>published_date__lte=timezone.now()</code>
    and orders by <code>published_date</code>, so drafts and future-dated posts stay off it
    (${cite(a.views.file, a.views.functions.find(f => f.name === 'published_posts')?.line)}). Writing a post, step by step:</p>
  ${writeFlow(a)}
  <p><code>${esc(a.form.name)}</code> (${cite(a.form.file, a.form.line)}) is a ModelForm on <code>${esc(a.form.model)}</code>
    exposing only <code>${esc(a.form.fields.join(', '))}</code>; the author and dates are set by the view.</p>
  <h2>4. Templates turn data into HTML</h2>
  <p>Every page extends <code>base.html</code> (orange header, Bootstrap 3 from a CDN, the Bungee font) and fills its
    <code>content</code> block. <code>linebreaksbr</code> turns newlines in a post's text into <code>&lt;br&gt;</code>.</p>
  ${templatesBlock(a)}
  <h2>5. Settings</h2>
  <div class="scroll"><table><tbody>${list(a.settings.settings, s => `<tr><td><code>${esc(s.name)}</code></td>
    <td class="mono small">${esc(s.value.length > 160 ? s.value.slice(0, 160) + ' ...' : s.value)}</td><td>${cite(a.settings.file, s.line)}</td></tr>`)}</tbody></table></div>`;
});
