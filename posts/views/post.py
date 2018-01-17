
from flask.json import jsonify
from flask.views import MethodView

from .. import db
from ..models import Post

from .base import HandleErrorMixin


class PostView(MethodView, HandleErrorMixin):
    def get(self, user_id):
        """Retrieve the posts associated with a user in the database."""

        with db.get_session() as DB:
            posts = DB.query(Post).filter(Post.user_id == user_id).all()

        return jsonify([p.to_dict() for p in posts])


def register(app, root, endpoint):
    """Add roots to an app at a specified root. Takes three parameters:

    - app: the app to which the routes should be added.
    - root: the URL root to use for all routes which are added.
    - endpoint: the name of the endpoint to be used for resolving URLs.

    """

    post_view = PostView.as_view(endpoint)

    app.add_url_rule(root, view_func=post_view, methods=["GET"])
