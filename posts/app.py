
from flask import Flask

from . import db
from .config import Config


def create_app():
    app = Flask("posts")
    app.config.from_object(Config)
    add_routes(app)
    return app


def init_db(app):
    db.init(app.config["DATABASE_PATH"])


def add_routes(app):
    @app.route("/")
    def root():
        return "Hello"
