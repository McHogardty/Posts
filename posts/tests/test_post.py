
import json

from ..db import get_session
from ..models import Post, User

from .base import AppTestCase


class TestPost(AppTestCase):
    def test_list_posts(self):
        """Test the API endpoint for listing posts associated with a user."""

        user1 = User(name="John", email="john@email.com")
        user2 = User(name="James", email="james@email.com")

        posts = [Post(title="Post 1", body="My first post.", user=user1),
                 Post(title="Post 2", body="A second post.", user=user1),
                 Post(title="Post 3", body="The third post I ever wrote.",
                      user=user2)]

        with get_session() as DB:
            DB.add(user1)
            DB.add(user2)
            DB.add_all(posts)

        rv = self.client.get("/api/user/{0}/post".format(user1.id))
        self.assertEqual(rv.status_code, 200)

        expected = [p.to_dict() for p in posts[:2]]
        self.assertEqual(json.loads(rv.data), expected)

    def test_list_posts_no_user(self):
        """Test the API endpoint for listing posts when a user does not exist
        in the database.

        """

        users = [User(name="Jill", email="jill@hill.com"),
                 User(name="Jack", email="jack@hiil.com")]

        with get_session() as DB:
            DB.add_all(users)

        rv = self.client.get("/api/user/{0}/post".format(users[-1].id + 312))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_view_post(self):
        """Test the API endpoint for viewing a post for a user."""

        user = User(name="Jill", email="jill@email.com")

        post = Post(title="Post", body="Some post body.", user=user)

        with get_session() as DB:
            DB.add(user)
            DB.add(post)

        rv = self.client.get("/api/user/{0}/post/{1}".format(user.id, post.id))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data), post.to_dict())

    def test_view_post_no_user(self):
        """Test the API endpoint for viewing a user's post where the user does
        not exist.

        """

        users = [User(name="Jill", email="jill@hill.com"),
                 User(name="Jack", email="jack@hiil.com")]

        with get_session() as DB:
            DB.add_all(users)

        rv = self.client.get("/api/user/{0}/post/1".format(users[-1].id + 723))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_view_post_no_post(self):
        """Test the endpoint for viewing a user's post where the post does not
        exist.

        """

        user = User(name="Michael", email="test@email.com")

        posts = [Post(title="First post", body="Post number one.", user=user),
                 Post(title="Second post", body="The second post", user=user)]

        with get_session() as DB:
            DB.add(user)
            DB.add_all(posts)

        rv = self.client.get("/api/user/{0}/post/{1}"
                             .format(user.id, posts[-1].id + 325))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such post found.")

    def test_create_post(self):
        """Test the endpoint for creation of posts."""

        user = User(name="Jill", email="jill@jill.com")

        with get_session() as DB:
            DB.add(user)

        data = {"title": "A post title", "body": "Something important."}

        rv = self.client.post("/api/user/{0}/post".format(user.id),
                              data=json.dumps(data))
        self.assertEqual(rv.status_code, 201)

        returned = json.loads(rv.data)
        self.assertEqual(returned["title"], data["title"])
        self.assertEqual(returned["body"], data["body"])

        with get_session() as DB:
            post = DB.query(Post).filter(User.id == user.id,
                                         Post.id == returned["id"]).one()

        self.assertEqual(post.title, data["title"])
        self.assertEqual(post.body, data["body"])

    def test_create_post_no_user(self):
        """Test the endpoint for post creation where the user does not exist in
        the database.

        """

        users = [User(name="Jill", email="jill@hill.com"),
                 User(name="Jack", email="jack@hiil.com")]

        with get_session() as DB:
            DB.add_all(users)

        data = {"title": "A post title", "body": "Something important."}

        rv = self.client.post("/api/user/{0}/post".format(users[-1].id + 500),
                              data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_create_post_no_data(self):
        """Test the endpoint for creation of posts when no data is provided."""

        user = User(name="Joe Bloggs", email="j.b@gmail.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.post("/api/user/{0}/post".format(user.id))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No data was provided.")

    def test_create_post_no_title(self):
        """Test the endpoint for creation of posts when data is missing."""

        user = User(name="John", email="john@john.com")

        with get_session() as DB:
            DB.add(user)

        data = {"body": "A prolific post body."}

        rv = self.client.post("/api/user/{0}/post".format(user.id),
                              data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No post title was provided.")

    def test_create_post_no_body(self):
        """Test the endpoint for creation of posts when data is missing."""

        user = User(name="Michael", email="email@test.com")

        with get_session() as DB:
            DB.add(user)

        data = {"title": "Title"}

        rv = self.client.post("/api/user/{0}/post".format(user.id),
                              data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No post body was provided.")

    def test_update_post(self):
        """Test the endpoint for updating a post."""

        user = User(name="Joe B", email="joe@email.com")

        post = Post(title="Wrong title", body="The correct body.",
                    user=user)

        with get_session() as DB:
            DB.add(user)
            DB.add(post)

        data = {"title": "Right title"}

        rv = self.client.put("/api/user/{0}/post/{1}".format(user.id, post.id),
                             data=json.dumps(data))
        self.assertEqual(rv.status_code, 200)

        returned = json.loads(rv.data)
        self.assertEqual(returned["id"], post.id)
        self.assertEqual(returned["title"], data["title"])
        self.assertEqual(returned["body"], post.body)

        with get_session() as DB:
            updated = DB.query(Post).filter(Post.id == returned["id"]).one()

        self.assertEqual(updated.title, data["title"])
        self.assertEqual(updated.body, post.body)

    def test_update_post_no_user(self):
        """Test the endpoint for updating a post when the user does not exist
        in the database.

        """

        users = [User(name="Jill", email="jill@hill.com"),
                 User(name="Jack", email="jack@hiil.com")]

        with get_session() as DB:
            DB.add_all(users)

        data = {"body": "A new body."}

        rv = self.client.put("/api/user/{0}/post/142"
                             .format(users[-1].id + 921),
                             data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_update_post_no_post(self):
        """Test the endpoint for updating a post when the post does not exist
        in the database.

        """

        user = User(name="Michael", email="test@email.com")

        posts = [Post(title="First post", body="Post number one.", user=user),
                 Post(title="Second post", body="The second post", user=user)]

        with get_session() as DB:
            DB.add(user)
            DB.add_all(posts)

        data = {"body": "A new post body."}

        rv = self.client.put("/api/user/{0}/post/{1}"
                             .format(user.id, posts[-1].id + 637),
                             data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such post found.")

    def test_update_post_no_data(self):
        """Test the endpoint for updating a post when no data is provided."""

        user = User(name="John Smith", email="john@apple.com")

        post = Post(title="New", body="My newest post.", user=user)

        with get_session() as DB:
            DB.add(user)
            DB.add(post)

        rv = self.client.put("/api/user/{0}/post/{1}".format(user.id, post.id))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No data was provided.")

        rv = self.client.put("/api/user/{0}/post/{1}".format(user.id, post.id),
                             data="{}")
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No data was provided.")

    def test_delete_post(self):
        """Test the endpoint for deleting a post."""

        user = User(name="Jill Bloggs", email="jill.bloggs@gmail.com")

        post = Post(title="Bad post", body="This post will be deleted.",
                    user=user)

        with get_session() as DB:
            DB.add(user)
            DB.add(post)

        rv = self.client.delete("/api/user/{0}/post/{1}"
                                .format(user.id, post.id))
        self.assertEqual(rv.status_code, 204)
