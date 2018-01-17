
import json

from ..db import get_session
from ..models import User

from .base import AppTestCase


class TestRoot(AppTestCase):
    def test_root(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(b"Hello", rv.data)


class TestUser(AppTestCase):
    def test_list_all_users(self):
        users = [User(name="Michael", email="michael@test.com"),
                 User(name="Jill Smith", email="jill@test.com"),
                 User(name="John", email="john@gmail.com")]

        with get_session() as DB:
            DB.add_all(users)

        rv = self.client.get("/user")
        self.assertEqual(rv.status_code, 200)

        expected = [u.to_dict() for u in users]
        self.assertEqual(json.loads(rv.data), expected)
