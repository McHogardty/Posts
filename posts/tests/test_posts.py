
import json

from ..db import get_session
from ..models import Post, User

from .base import AppTestCase


class TestRoot(AppTestCase):
    def test_root(self):
        """Test the root endpoint."""

        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(b"Hello", rv.data)


class TestUser(AppTestCase):
    def test_list_all_users(self):
        """Test the API endpoint for retrieving a list of users"""

        users = [User(name="Michael", email="michael@test.com"),
                 User(name="Jill Smith", email="jill@test.com"),
                 User(name="John", email="john@gmail.com")]

        with get_session() as DB:
            DB.add_all(users)

        rv = self.client.get("/user")
        self.assertEqual(rv.status_code, 200)

        expected = [u.to_dict() for u in users]
        self.assertEqual(json.loads(rv.data), expected)

    def test_list_user(self):
        """Test the endpoint for retrieving a single user."""

        user = User(name="Jill Smith", email="jill@test.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.get("/user/{0}".format(user.id))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data), user.to_dict())

    def test_list_user_no_user(self):
        """Test the endpoint for retrieving a single user if no user exists."""

        rv = self.client.get("/user/207")
        self.assertEqual(rv.status_code, 404)

    def test_create_user(self):
        """Test the endpoint for creating a user."""

        data = {"name": "Michael", "email": "michael@gmail.com"}

        rv = self.client.post("/user", data=json.dumps(data))
        self.assertEqual(rv.status_code, 201)

        returned = json.loads(rv.data)
        self.assertEqual(data["name"], returned["name"])
        self.assertEqual(data["email"], returned["email"])

        with get_session() as DB:
            u = DB.query(User).filter(User.id == returned["id"]).one()

        self.assertEqual(data["name"], u.name)
        self.assertEqual(data["email"], u.email)

    def test_create_user_no_data(self):
        """Test the endpoint for creating a user if no data is provided."""

        rv = self.client.post("/user")
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No data was provided.")

    def test_create_user_no_name(self):
        """Test the endpoint for creating a user when no name is provided."""

        data = {"email": "joe@bloggs.com"}

        rv = self.client.post("/user", data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No name was provided.")

    def test_create_user_no_email(self):
        """Test the endpoint for creating a user when no email is provided."""

        data = {"name": "Testy testerson."}

        rv = self.client.post("/user", data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No email was provided.")

    def test_update_user(self):
        """Test the endpoint for updating a user."""

        user = User(name="John", email="incorrect@wrong.com")

        with get_session() as DB:
            DB.add(user)

        data = {"email": "correct@email.com"}

        rv = self.client.put("/user/{0}".format(user.id),
                             data=json.dumps(data))
        self.assertEqual(rv.status_code, 200)

        returned = json.loads(rv.data)
        self.assertEqual(returned["id"], user.id)
        self.assertEqual(returned["name"], user.name)
        self.assertEqual(returned["email"], data["email"])

        with get_session() as DB:
            updated = DB.query(User).filter(User.id == user.id).one()

        self.assertEqual(updated.name, user.name)
        self.assertEqual(updated.email, data["email"])

    def test_update_user_no_user(self):
        """Test the endpoint for updating a user if no such user exists."""

        data = {"name": "New name"}

        rv = self.client.put("/user/501", data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)

    def test_update_user_no_data(self):
        """Test the endpoint for updating a user if no data is provided."""

        user = User(name="Michael", email="michael@test.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.put("/user/{0}".format(user.id))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No data was provided.")

        rv = self.client.put("/user/{0}".format(user.id), data="{}")
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No data was provided.")

    def test_delete_user(self):
        """Test the endpoint for deleting a user."""

        user = User(name="Jill", email="jill@mail.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.delete("/user/{0}".format(user.id))
        self.assertEqual(rv.status_code, 200)

        with get_session() as DB:
            x = DB.query(User).filter(User.id == user.id).first()

        self.assertIsNone(x)


class TestPost(AppTestCase):
    def test_list_posts(self):
        """Test the API endpoint for listing posts associated with a user."""

        user = User(name="John", email="john@email.com")

        posts = [Post(title="Post 1", body="My first post."),
                 Post(title="Post 2", body="A second post."),
                 Post(title="Post 3", body="The third post I ever wrote.")]

        with get_session() as DB:
            DB.add(user)
            for p in posts:
                p.user = user
                DB.add(p)

        rv = self.client.get("/user/{0}/post".format(user.id))
        self.assertEqual(rv.status_code, 200)

        expected = [p.to_dict() for p in posts]
        self.assertEqual(json.loads(rv.data), expected)

    def test_list_posts_no_user(self):
        """Test the API endpoint for listing posts when a user does not exist
        in the database.

        """

        rv = self.client.get("/user/213/post")
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_view_post(self):
        """Test the API endpoint for viewing a post for a user."""

        user = User(name="Jill", email="jill@email.com")

        post = Post(title="Post", body="Some post body.", user=user)

        with get_session() as DB:
            DB.add(user)
            DB.add(post)

        rv = self.client.get("/user/{0}/post/{1}".format(user.id, post.id))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data), post.to_dict())

    def test_view_post_no_user(self):
        """Test the API endpoint for viewing a user's post where the user does
        not exist.

        """

        rv = self.client.get("/user/321/post/1")
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_view_post_no_post(self):
        """Test the endpoint for viewing a user's post where the post does not
        exist.

        """

        user = User(name="Michael", email="test@email.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.get("/user/{0}/post/231".format(user.id))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such post found.")

    def test_create_post(self):
        """Test the endpoint for creation of posts."""

        user = User(name="Jill", email="jill@jill.com")

        with get_session() as DB:
            DB.add(user)

        data = {"title": "A post title", "body": "Something important."}

        rv = self.client.post("/user/{0}/post".format(user.id),
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

        data = {"title": "A post title", "body": "Something important."}

        rv = self.client.post("/user/702/post", data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_create_post_no_data(self):
        """Test the endpoint for creation of posts when no data is provided."""

        user = User(name="Joe Bloggs", email="j.b@gmail.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.post("/user/{0}/post".format(user.id))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No data was provided.")

    def test_create_post_no_title(self):
        """Test the endpoint for creation of posts when data is missing."""

        user = User(name="John", email="john@john.com")

        with get_session() as DB:
            DB.add(user)

        data = {"body": "A prolific post body."}

        rv = self.client.post("/user/{0}/post".format(user.id),
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

        rv = self.client.post("/user/{0}/post".format(user.id),
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

        rv = self.client.put("/user/{0}/post/{1}".format(user.id, post.id),
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

        data = {"body": "A new body."}

        rv = self.client.put("/user/842/post/142", data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(json.loads(rv.data)["error"], "No such user found.")

    def test_update_post_no_data(self):
        """Test the endpoint for updating a post when no data is provided."""

        user = User(name="John Smith", email="john@apple.com")

        post = Post(title="New", body="My newest post.", user=user)

        with get_session() as DB:
            DB.add(user)
            DB.add(post)

        rv = self.client.put("/user/{0}/post/{1}".format(user.id, post.id))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No data was provided.")

        rv = self.client.put("/user/{0}/post/{1}".format(user.id, post.id),
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

        rv = self.client.delete("/user/{0}/post/{1}".format(user.id, post.id))
        self.assertEqual(rv.status_code, 200)
