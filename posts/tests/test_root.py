
import json

from .base import AppTestCase


class TestRoot(AppTestCase):
    def test_root(self):
        """Test the root endpoint for the app."""

        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, b"Hello")

    def test_api_root(self):
        """Test the root endpoint."""

        rv = self.client.get("/api")
        self.assertEqual(rv.status_code, 200)
        with self.app.app_context():
            self.assertEqual(json.loads(rv.data)["links"],
                             {"user": "/api/user"})
