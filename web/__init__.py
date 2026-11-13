"""Web interface for the Django Girls blog (FastAPI shell + static GitHub Pages export).

Contents:
    app.py           FastAPI app: JSON API under /api, the front end in static/, the real Django blog at /django/
    django_setup.py  configure Django with mysite.settings_demo and build/seed the demo database
    demo_posts.py    the labelled demo posts (one per 2017 commit of this repo, plus one unpublished draft)
    blog_data.py     posts as JSON, using blog.views.published_posts and Django's own template filters
    anatomy.py       "How this Django app works": models, urls, views, templates, settings read from the real code
    code_index.py    code explorer: file tree, contents, header summaries (secrets redacted)
    static/          the ES-module front end (no build step)
"""
