from django.contrib.auth.models import User
from django.test import TestCase

from forums.models import Post, Topic


class TestIndex(TestCase):
    fixtures = ["tests/forum.json"]

    def test_get(self):
        response = self.client.get("/forums/")
        self.assertEqual(response.status_code, 200)


class TestNewTopic(TestCase):
    fixtures = ["tests/forum.json"]

    def setUp(self):
        User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_get(self):
        response = self.client.get("/forums/new/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(
            "/forums/new/", {"title": "I'm off to the shops", "body": "does anyone need anything"}
        )
        topic = Topic.objects.get(title="I'm off to the shops")
        self.assertRedirects(response, "/forums/%d/" % topic.id)

    def test_post_overlong(self):
        response = self.client.post("/forums/new/", {"title": "Amig" + ("a" * 1000), "body": "I am very original."})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ensure this value has at most 255 characters")


class TestShowTopic(TestCase):
    fixtures = ["tests/forum.json"]

    def test_get(self):
        response = self.client.get("/forums/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "fix me beautifull")
        self.assertContains(response, "to reply")
        self.assertNotContains(response, "Add a reply")

    def test_get_specific_post(self):
        response = self.client.get("/forums/post/1/")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_gets_form(self):
        User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        response = self.client.get("/forums/post/1/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "to reply")
        self.assertContains(response, "Add a reply")

    def test_locked_topic_for_non_logged_in_user(self):
        Topic.objects.filter(id=1).update(locked=True)
        response = self.client.get("/forums/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This topic is locked.")
        self.assertNotContains(response, "to reply")
        self.assertNotContains(response, "Add a reply")

    def test_locked_topic_for_ordinary_user(self):
        Topic.objects.filter(id=1).update(locked=True)
        User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        response = self.client.get("/forums/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This topic is locked.")
        self.assertNotContains(response, "to reply")
        self.assertNotContains(response, "Add a reply")

    def test_locked_topic_for_admin(self):
        Topic.objects.filter(id=1).update(locked=True)
        User.objects.create_user(username="testuser", email="testuser@example.com", password="12345", is_staff=True)
        self.client.login(username="testuser", password="12345")
        response = self.client.get("/forums/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "(but you can reply anyway because you're an admin)")
        self.assertContains(response, "Add a reply")


class TestTopicReply(TestCase):
    fixtures = ["tests/forum.json"]

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_get(self):
        response = self.client.get("/forums/1/reply/")
        self.assertEqual(response.status_code, 200)

    def test_empty_post(self):
        response = self.client.post(
            "/forums/1/reply/",
            {
                "body": "",
            },
        )
        self.assertEqual(Topic.objects.get(id=1).reply_count, 0)
        self.assertEqual(Post.objects.filter(body="").count(), 0)
        self.assertRedirects(response, "/forums/1/")

    def test_post(self):
        response = self.client.post(
            "/forums/1/reply/",
            {
                "body": "it's only a bit broken",
            },
        )
        self.assertEqual(Topic.objects.get(id=1).reply_count, 1)
        post = Post.objects.get(body="it's only a bit broken")
        self.assertRedirects(response, "/forums/1/#post-%d" % post.id)

    def test_locked(self):
        Topic.objects.filter(id=1).update(locked=True)
        response = self.client.post(
            "/forums/1/reply/",
            {
                "body": "it's only a bit broken",
            },
        )
        self.assertEqual(Topic.objects.get(id=1).reply_count, 0)
        self.assertRedirects(response, "/forums/1/")
        response = self.client.get("/forums/1/")
        self.assertContains(response, "This topic is locked")

    def test_locked_for_admin(self):
        Topic.objects.filter(id=1).update(locked=True)
        self.user.is_staff = True
        self.user.save()
        response = self.client.post(
            "/forums/1/reply/",
            {
                "body": "it's only a bit broken",
            },
        )
        self.assertEqual(Topic.objects.get(id=1).reply_count, 1)
        post = Post.objects.get(body="it's only a bit broken")
        self.assertRedirects(response, "/forums/1/#post-%d" % post.id)


class TestDeletePost(TestCase):
    fixtures = ["tests/forum.json"]

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="12345", is_staff=True
        )
        self.client.login(username="testuser", password="12345")
        self.topic = Topic.objects.get(id=1)

    def add_reply(self):
        self.post = Post.objects.create(topic=self.topic, user=self.user, body="it's only a bit broken")
        self.topic.reply_count = 1
        self.topic.last_post_by_user = self.user
        self.topic.last_post_at = self.post.created_at
        self.topic.save()

    def test_get(self):
        self.add_reply()
        response = self.client.get("/forums/post/%d/delete/" % self.post.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.add_reply()
        response = self.client.post(
            "/forums/post/%d/delete/" % self.post.id,
            {"yes": "yes"},
        )
        self.assertRedirects(response, "/forums/1/")
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.reply_count, 0)
        self.assertEqual(self.topic.last_post_by_user.pk, 1)
        self.assertEqual(self.topic.last_post_at, Post.objects.get(id=1).created_at)

    def test_delete_requires_admin_privileges(self):
        self.add_reply()
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(
            "/forums/post/%d/delete/" % self.post.id,
            {"yes": "yes"},
        )
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())
        self.assertRedirects(response, "/forums/post/%d/#post-%d" % (self.post.id, self.post.id))

    def test_delete_topic_when_last_post_deleted(self):
        self.post = self.topic.posts.first()
        response = self.client.post(
            "/forums/post/%d/delete/" % self.post.id,
            {"yes": "yes"},
        )
        self.assertRedirects(response, "/forums/")
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
        self.assertFalse(Topic.objects.filter(id=self.topic.id).exists())


class TestEditPost(TestCase):
    fixtures = ["tests/forum.json"]

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="12345", is_staff=True
        )
        self.client.login(username="testuser", password="12345")
        self.topic = Topic.objects.get(id=1)

    def add_reply(self):
        self.post = Post.objects.create(topic=self.topic, user=self.user, body="it's only a bit broken")
        self.topic.reply_count = 1
        self.topic.last_post_by_user = self.user
        self.topic.last_post_at = self.post.created_at
        self.topic.save()

    def test_get(self):
        self.add_reply()
        response = self.client.get("/forums/post/%d/edit/" % self.post.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.add_reply()
        response = self.client.post(
            "/forums/post/%d/edit/" % self.post.id,
            {"body": "it's only somewhat broken"},
        )
        self.assertRedirects(response, "/forums/post/%d/#post-%d" % (self.post.id, self.post.id))
        self.post.refresh_from_db()
        self.assertEqual(self.post.body, "it's only somewhat broken")

    def test_post_invalid(self):
        self.add_reply()
        response = self.client.post(
            "/forums/post/%d/edit/" % self.post.id,
            {"body": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.body, "it's only a bit broken")

    def test_edit_requires_admin_privileges(self):
        self.add_reply()
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(
            "/forums/post/%d/edit/" % self.post.id,
            {"body": "it's only somewhat broken"},
        )
        self.assertRedirects(response, "/forums/post/%d/#post-%d" % (self.post.id, self.post.id))
        self.post.refresh_from_db()
        self.assertEqual(self.post.body, "it's only a bit broken")
