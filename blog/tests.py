"""Tests for the blog app. Run: python manage.py test blog"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post


class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("writer", password="not-a-real-password-123")
        self.post = Post.objects.create(author=self.user, title="Hello", text="line one\nline two")

    def test_str_is_title(self):
        self.assertEqual(str(self.post), "Hello")

    def test_publish_sets_date(self):
        self.assertIsNone(self.post.published_date)
        self.post.publish()
        self.assertIsNotNone(Post.objects.get(pk=self.post.pk).published_date)

    def test_list_shows_only_published(self):
        Post.objects.create(author=self.user, title="Later", text="x",
                            published_date=timezone.now() + timedelta(days=1))
        self.post.publish()
        r = self.client.get(reverse("post_list"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Hello")
        self.assertContains(r, "line one<br>line two")
        self.assertNotContains(r, "Later")

    def test_detail(self):
        r = self.client.get(reverse("post_detail", kwargs={"pk": self.post.pk}))
        self.assertContains(r, "<h1>Hello</h1>")
        self.assertEqual(self.client.get("/post/999/").status_code, 404)

    def test_logged_in_user_can_create_and_edit(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("post_new"), {"title": "New", "text": "body"})
        new = Post.objects.get(title="New")
        self.assertRedirects(r, reverse("post_detail", kwargs={"pk": new.pk}))
        self.assertIsNotNone(new.published_date)
        self.client.post(reverse("post_edit", kwargs={"pk": new.pk}), {"title": "New 2", "text": "body"})
        self.assertEqual(Post.objects.get(pk=new.pk).title, "New 2")
