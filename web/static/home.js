// Home: hero, real counts, cards to the other pages.
import { api, app, esc, isStatic, route } from './core.js';

route('home', async () => {
  const i = await api('/info');
  const live = isStatic() ? '' : '<a class="btn alt" href="django/">Open the live Django blog</a>';
  app().innerHTML = `
  <section class="hero">
    <p class="kicker">Django Girls tutorial · December 2017</p>
    <h1 class="glow">George's Blog</h1>
    <p class="lead">A small Django blog built by following the Django Girls tutorial: one <code>Post</code> model, four
      URL patterns, four views and four templates. Here you can read it, see how a request travels through the code,
      try Django's URL resolver and browse every file.</p>
    <a class="btn" href="#/blog">Read the blog</a><a class="btn alt" href="#/how">How it works</a>${live}
  </section>
  <div class="tiles">
    <div class="tile"><b>${i.posts}</b><span>demo posts (${i.published} published)</span></div>
    <div class="tile"><b>${i.url_patterns}</b><span>URL patterns</span></div>
    <div class="tile"><b>${i.views}</b><span>functions in views.py</span></div>
    <div class="tile"><b>${i.templates}</b><span>templates</span></div>
    <div class="tile"><b>${i.app_lines}</b><span>lines in ${i.app_files} app files</span></div>
    <div class="tile"><b>${esc(i.django)}</b><span>Django version it runs on</span></div>
  </div>
  <div class="grid">
    <a class="card" href="#/blog"><b>The blog</b><small>post_list and post_detail, read-only</small>
      <span>The front page as the Django view selects it: published posts, oldest first. The posts are labelled demo posts, one per 2017 commit.</span></a>
    <a class="card" href="#/how"><b>How this Django app works</b><small>models · urls · views · templates</small>
      <span>A request's journey, drawn and explained from the real code with file and line for every step.</span></a>
    <a class="card" href="#/router"><b>URL router</b><small>Django's resolver in your browser</small>
      <span>Type a path and watch it matched against the patterns, exactly as Django does (the tests check it against Django's own resolver).</span></a>
    <a class="card" href="#/code"><b>Code explorer</b><small>${i.files} files · ${i.lines} lines</small>
      <span>Every file with line numbers, highlighting, and search by name or text.</span></a>
    <a class="card" href="#/about"><b>About</b><small>run it yourself</small>
      <span>What it is, how to run the Django app and this web interface, credits and licence.</span></a>
  </div>`;
});
