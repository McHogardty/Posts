
import json

from ..db import get_session
from ..models import Post, User

from .base import AppTestCase


class TestUser(AppTestCase):
    def test_list_all_users(self):
        """Test the API endpoint for retrieving a list of users"""

        users = [User(name="Michael", email="michael@test.com"),
                 User(name="Jill Smith", email="jill@test.com"),
                 User(name="John", email="john@gmail.com")]

        with get_session() as DB:
            DB.add_all(users)

        rv = self.client.get("/api/user")
        self.assertEqual(rv.status_code, 200)

        expected = [u.to_dict() for u in users]
        self.assertEqual(json.loads(rv.data), expected)

    def test_list_user(self):
        """Test the endpoint for retrieving a single user."""

        user = User(name="Jill Smith", email="jill@test.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.get("/api/user/{0}".format(user.id))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data), user.to_dict())

    def test_list_user_no_user(self):
        """Test the endpoint for retrieving a single user if no user exists."""

        users = [User(name="Michael", email="michael@test.com"),
                 User(name="Jill Smith", email="jill@test.com")]

        with get_session() as DB:
            DB.add_all(users)

        rv = self.client.get("/api/user/{0}".format(users[-1].id + 834))
        self.assertEqual(rv.status_code, 404)

    def test_create_user(self):
        """Test the endpoint for creating a user."""

        data = {"name": "Michael", "email": "michael@gmail.com"}

        rv = self.client.post("/api/user", data=json.dumps(data))
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

        rv = self.client.post("/api/user")
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No data was provided.")

    def test_create_user_no_name(self):
        """Test the endpoint for creating a user when no name is provided."""

        data = {"email": "joe@bloggs.com"}

        rv = self.client.post("/api/user", data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"], "No name was provided.")

    def test_create_user_no_email(self):
        """Test the endpoint for creating a user when no email is provided."""

        data = {"name": "Testy testerson."}

        rv = self.client.post("/api/user", data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No email was provided.")

    def test_create_user_bad_email(self):
        """Test the endpoint for creating a user where an invalid email is
        provided.

        """

        data = {"name": "John Smith", "email": "notanemail"}

        rv = self.client.post("/api/user", data=json.dumps(data))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "An invalid email was provided.")

    def test_update_user(self):
        """Test the endpoint for updating a user."""

        user = User(name="John", email="incorrect@wrong.com")

        with get_session() as DB:
            DB.add(user)

        data = {"email": "correct@email.com"}

        rv = self.client.put("/api/user/{0}".format(user.id),
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

        users = [User(name="Michael", email="michael@test.com"),
                 User(name="Jill Smith", email="jill@test.com")]

        with get_session() as DB:
            DB.add_all(users)

        data = {"name": "New name"}

        rv = self.client.put("/api/user/{0}".format(users[-1].id + 824),
                             data=json.dumps(data))
        self.assertEqual(rv.status_code, 404)

    def test_update_user_no_data(self):
        """Test the endpoint for updating a user if no data is provided."""

        user = User(name="Michael", email="michael@test.com")

        with get_session() as DB:
            DB.add(user)

        rv = self.client.put("/api/user/{0}".format(user.id))
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No data was provided.")

        rv = self.client.put("/api/user/{0}".format(user.id), data="{}")
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(json.loads(rv.data)["error"],
                         "No data was provided.")

    def test_delete_user(self):
        """Test the endpoint for deleting a user."""

        user = User(name="Jill", email="jill@mail.com")

        posts = [Post(title="First", body="The first post.", user=user),
                 Post(title="Second", body="The second post.", user=user)]

        with get_session() as DB:
            DB.add(user)
            DB.add_all(posts)

        rv = self.client.delete("/api/user/{0}".format(user.id))
        self.assertEqual(rv.status_code, 204)

        with get_session() as DB:
            x = DB.query(User).filter(User.id == user.id).first()
            y = DB.query(Post).filter(Post.user == user).all()

        self.assertIsNone(x)
        self.assertFalse(y)
