
from flask import Flask
from flask.json import jsonify

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

    views.user.register(app, "/user", "users")
