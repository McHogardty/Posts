
import os
import tempfile
from unittest import TestCase

from posts.app import create_app, init_db


class AppTestCase(TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.db_fd, self.app.config["DATABASE_PATH"] = tempfile.mkstemp()
        self.client = self.app.test_client()
        init_db(self.app)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.app.config["DATABASE_PATH"])


class TestRoot(AppTestCase):
    def test_root(self):
        rv = self.client.get("/")
        self.assertEqual(b"Hello", rv.data)
