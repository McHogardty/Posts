"""Logic related to creation and configuration of app instances."""

from flask import Flask, url_for
from flask.json import jsonify

from . import db, views
from .config import Config


def create_app():
    """Create a new instance of the app and configure it."""

    app = Flask("posts")
    app.config.from_object(Config)
    add_routes(app)
    return app


def init_db(app):
    """Initialise the database engine"""

    db.init(app.config["DATABASE_PATH"])


def add_routes(app):
    """Create the routes for an app instance."""

    @app.route("/")
    def root():
        return "Hello"

    @app.route("/api")
    def api_root():
        return jsonify({"links": {"user": url_for("users.list")}})

    # Remove the default HTML.
    @app.errorhandler(404)
    def handle401(e):
        r = jsonify("")
        r.status_code = 404
        return r

    @app.errorhandler(500)
    def handle500(e):
        r = jsonify("")
        r.status_code = 500
        return r

    views.user.register(app, "/api/user", "users")
    views.post.register(app, "/api/user/<int:user_id>/post", "posts")
