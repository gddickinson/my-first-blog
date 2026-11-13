"""Blog posts as JSON, produced with the blog's own query (blog.views.published_posts) and Django's own
template filters, so the web pages show what the Django templates would."""
from django.template.defaultfilters import linebreaksbr
from django.urls import reverse
from django.utils import formats, timezone

from blog.models import Post
from blog.views import published_posts


def _when(dt):
    """The text {{ post.published_date }} renders: DATETIME_FORMAT in settings.TIME_ZONE."""
    return formats.date_format(timezone.localtime(dt), "DATETIME_FORMAT") if dt else None


def post_json(post: Post, front_ids=()) -> dict:
    return {
        "pk": post.pk, "title": post.title, "author": post.author.username,
        "created": post.created_date.isoformat(), "created_text": _when(post.created_date),
        "published": post.published_date.isoformat() if post.published_date else None,
        "published_text": _when(post.published_date),
        "on_front_page": post.pk in front_ids,
        "html": str(linebreaksbr(post.text, autoescape=True)),
        "django_url": reverse("post_detail", kwargs={"pk": post.pk}),
    }


def posts() -> dict:
    front = list(published_posts())
    ids = {p.pk for p in front}
    others = Post.objects.exclude(pk__in=ids).order_by("pk")
    return {
        "front_page": [post_json(p, ids) for p in front],
        "not_on_front_page": [post_json(p, ids) for p in others],
        "query": "Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')",
    }


def post(pk: int) -> dict | None:
    p = Post.objects.filter(pk=pk).first()
    if p is None:
        return None
    return post_json(p, {q.pk for q in published_posts()})
