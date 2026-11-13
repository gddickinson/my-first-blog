// The blog, read-only: #/blog is post_list, #/post/<pk> is post_detail. Text and dates are what the Django templates
// render (linebreaksbr and DATETIME_FORMAT applied by Django in web/blog_data.py).
import { api, app, esc, isStatic, list, route } from './core.js';

const frame = body => `<div class="blogframe"><div class="page-header"><a href="#/blog">George's Blog</a></div>
  <div class="content">${body}</div></div>`;
const demoNote = `<p class="callout small">These are <b>demo posts</b>, not posts George wrote: the repository holds no
  blog database, so the web interface makes one with the blog's own migrations and adds one labelled post per commit
  of 14 December 2017 (<code>web/demo_posts.py</code>).</p>`;
const liveLink = p => isStatic() ? '' : ` · <a href="django${esc(p.django_url)}">as Django renders it</a>`;

function postBlock(p, link = true) {
  const title = link ? `<a href="#/post/${p.pk}">${esc(p.title)}</a>` : esc(p.title);
  return `<div class="post${p.published ? '' : ' draft'}">
    ${p.published_text ? `<div class="date">${esc(p.published_text)}</div>` : '<div class="date">not published</div>'}
    <h2>${title}</h2><p>${p.html}</p></div>`;
}

route('blog', async () => {
  const d = await api('/posts');
  app().innerHTML = `
  <p class="kicker">post_list · blog/views.py</p><h1>The blog</h1>
  <p class="lead">The front page shows what <code>post_list</code> selects:
    <code>${esc(d.query)}</code>, so published posts, oldest first.</p>
  ${demoNote}
  ${frame(list(d.front_page, p => postBlock(p)))}
  <h2>Not on the front page</h2>
  <p>${d.not_on_front_page.length} post(s) without a past <code>published_date</code>. They still have their own
    URL, because <code>post_detail</code> looks posts up by primary key only.</p>
  ${list(d.not_on_front_page, p => `<p><a href="#/post/${p.pk}">${esc(p.title)}</a> <span class="demo-badge">draft</span></p>`)}`;
});

route('post', async ([pk]) => {
  const p = await api('/posts/' + encodeURIComponent(pk));
  app().innerHTML = `
  <p class="kicker">post_detail · /post/${p.pk}/</p>
  <p class="small"><a href="#/blog">&larr; all posts</a>${liveLink(p)} · <span class="demo-badge">demo post</span></p>
  ${frame(postBlock(p, false))}
  <div class="panel small"><dl class="kv">
    <dt>pk</dt><dd>${p.pk}</dd><dt>author</dt><dd>${esc(p.author)} (demo user, no password)</dd>
    <dt>created_date</dt><dd>${esc(p.created)}</dd><dt>published_date</dt><dd>${esc(p.published ?? 'None')}</dd>
    <dt>on front page</dt><dd>${p.on_front_page ? 'yes' : 'no'}</dd>
    <dt>Django URL</dt><dd>${esc(p.django_url)} (<a href="#/router?path=${encodeURIComponent(p.django_url)}">resolve it</a>)</dd>
  </dl></div>`;
});
