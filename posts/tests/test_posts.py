
import json

from ..db import get_session
from ..models import User

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
            new = DB.query(User).filter(User.id == user.id).one()

        self.assertEqual(new.name, user.name)
        self.assertEqual(new.email, data["email"])

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
