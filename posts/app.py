
from flask import Flask

from . import db, views
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

    views.user.register(app, "/user", "users")

    # @app.route("/user")
    # def list_users():
    #     with db.get_session() as DB:
    #         return jsonify([u.to_dict() for u in DB.query(User).all()])
