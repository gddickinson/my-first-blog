// About: what it is, how to run it, credits.
import { api, app, esc, route } from './core.js';

route('about', async () => {
  const i = await api('/info');
  app().innerHTML = `
  <p class="kicker">About</p><h1>George's Blog</h1>
  <p class="lead">The blog George built on 14 December 2017 while following the
    <a href="https://tutorial.djangogirls.org/" target="_blank" rel="noopener">Django Girls tutorial</a>
    (${i.commits_2017} commits that afternoon). Its settings list <code>gdickinson.pythonanywhere.com</code> as a host,
    where the tutorial deploys it. An earlier attempt from 2016 is in
    <a href="https://github.com/gddickinson/my-first-blog_old">my-first-blog_old</a>.</p>
  <h2>Run the Django app</h2>
  <pre>pip install Django==${esc(i.django)}
python manage.py migrate
python manage.py createsuperuser   # to log in and write posts
python manage.py runserver         # http://127.0.0.1:8000</pre>
  <p>The code was written for Django 1.11, which no longer runs on current Python; in 2026 it was moved to Django
    ${esc(i.django)} with the smallest changes possible (see the README). <code>SECRET_KEY</code> now comes from the
    <code>DJANGO_SECRET_KEY</code> environment variable.</p>
  <h2>Run this web interface</h2>
  <pre>pip install -r requirements-web.txt
python run_web.py                  # http://127.0.0.1:8256 (the real blog at /django/)</pre>
  <p>The web interface uses its own demo database (<code>.web_demo/</code>), made by the blog's migrations and filled
    with clearly labelled demo posts, one per commit of December 2017. The repository contains no real posts. The
    static site on GitHub Pages is the same front end with those posts exported to JSON, so it is read-only.</p>
  <h2>Credits</h2>
  <p>Code by George Dickinson, following the Django Girls tutorial. MIT licence (see LICENSE). The original pages use
    Bootstrap 3.2 and the Google font Bungee from their CDNs; this web interface uses no external files.</p>`;
});
