"""Demo posts for the web interface. They are NOT blog posts George wrote.

The repository holds no posts (db.sqlite3 is git-ignored), so the demo database gets one labelled post
per 2017 commit of this repository, dated at that commit and quoting its message and changed files
(from `git log --name-status`), plus one unpublished draft that shows the front-page filter at work.
"""
from datetime import datetime

# (commit, author date, message, files changed) from `git log --reverse --name-status` on master.
COMMITS = [
    ("9ce0557", "2017-12-14T12:54:27-07:00", "My Django Girls app, first commit",
     "added .gitignore, blog/ (admin, apps, migrations/0001_initial, models, tests, views), manage.py, mysite/"),
    ("42d6e12", "2017-12-14T15:43:42-07:00", "Changed the HTML for the site.",
     "added blog/templates/blog/post_list.html, blog/urls.py; changed blog/views.py, mysite/urls.py"),
    ("a7f1ae4", "2017-12-14T16:09:37-07:00", "Modified templates to display posts from database.",
     "changed blog/templates/blog/post_list.html"),
    ("b1101bf", "2017-12-14T16:41:25-07:00", "Font changes.",
     "added blog/static/css/blog.css; changed post_list.html, blog/views.py"),
    ("c60f428", "2017-12-14T17:05:28-07:00",
     "Added view and template for detailed blog post as well as CSS for the site.",
     "added base.html, post_detail.html; changed post_list.html, blog/urls.py, blog/views.py"),
    ("f8b24e9", "2017-12-14T17:31:58-07:00", "Added views to create/edit blog post inside the site.",
     "added blog/forms.py, post_edit.html; changed base.html, post_detail.html, blog/urls.py, blog/views.py"),
]
DEMO_USER = "demo"
DRAFT_TITLE = "[Demo] Unpublished draft"


def demo_posts():
    """(title, text, created, published) for every demo post; published is None for the draft."""
    out = []
    for i, (sha, when, msg, files) in enumerate(COMMITS, 1):
        dt = datetime.fromisoformat(when)
        text = (f"Demo post {i} of {len(COMMITS)}, seeded by web/demo_posts.py: not a post George wrote.\n"
                f"It is dated at commit {sha} of this repository, whose message was:\n"
                f"\"{msg}\"\nFiles: {files}.")
        out.append((f"[Demo] Step {i}: {msg}", text, dt, dt))
    last = datetime.fromisoformat(COMMITS[-1][1])
    out.append((DRAFT_TITLE,
                "Demo draft with no published_date. post_list() only shows posts whose published_date is set and "
                "not in the future, so this one is reachable at its own URL but missing from the front page.",
                last, None))
    return out


def seed() -> int:
    """Add the demo user and posts to an empty database; returns the number of posts added."""
    from django.contrib.auth.models import User

    from blog.models import Post
    if Post.objects.exists():
        return 0
    user, created = User.objects.get_or_create(username=DEMO_USER, defaults={"first_name": "Demo"})
    if created:
        user.set_unusable_password()
        user.save()
    for title, text, created_at, published in demo_posts():
        Post.objects.create(author=user, title=title, text=text, created_date=created_at,
                            published_date=published)
    return len(demo_posts())
