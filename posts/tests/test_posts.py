

from .base import AppTestCase


class TestRoot(AppTestCase):
    def test_root(self):
        rv = self.client.get("/")
        self.assertEqual(b"Hello", rv.data)
