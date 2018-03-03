
from flask import request
from flask.json import jsonify, loads
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from .. import db
from ..models import Post, User

from .base import HandleErrorMixin


class PostView(MethodView, HandleErrorMixin):
    def get(self, user_id, post_id):
        """Retrieve the posts associated with a user in the database. Takes
        two arguments:

        - user_id: The ID of the user who owns the post.
        - post_id: The ID of the post to be returned, or None if all posts are
                   required.

        """

        with db.get_session() as DB:
            if not User.exists(DB, user_id):
                return self.error("No such user found.", 404)

            if post_id is not None:
                try:
                    post = Post.get(DB, post_id)
                except NoResultFound:
                    return self.error("No such post found.", 404)

                response = post.to_dict()
            else:
                posts = User.get(DB, user_id).posts

                response = [p.to_dict() for p in posts]

        return jsonify(response)

    def post(self, user_id):
        """Create a post for a user in the database. Takes one argument:

        - user_id: the ID of the user who will own the post.

        """

        if not request.data:
            return self.error("No data was provided.", 400)

        data = loads(request.data)

        title = data.get("title", "")
        body = data.get("body", "")

        if not title:
            return self.error("No post title was provided.", 400)
        if not body:
            return self.error("No post body was provided.", 400)

        with db.get_session() as DB:
            if not User.exists(DB, user_id):
                return self.error("No such user found.", 404)

            post = Post.create(DB, title=title, body=body, user_id=user_id)

        r = jsonify(post.to_dict())
        r.status_code = 201
        return r

    def put(self, user_id, post_id):
        """Updated a post for a user in the database. Takes two arguments:

        - user_id: the ID of the user who owns the post.
        - post_id: the ID of the post to be updated.

        """

        if not request.data:
            return self.error("No data was provided.", 400)

        data = loads(request.data)

        title = data.get("title", "")
        body = data.get("body", "")

        if not title and not body:
            return self.error("No data was provided.", 400)

        updates = {}
        if title:
            updates["title"] = title
        if body:
            updates["body"] = body

        with db.get_session() as DB:
            if not User.exists(DB, user_id):
                return self.error("No such user found.", 404)

            try:
                post = Post.update_for_user(DB, post_id, user_id, **updates)
            except NoResultFound:
                return self.error("No such post found.", 404)

        return jsonify(post.to_dict())

    def delete(self, user_id, post_id):
        """Delete a post for a user in the database. Takes two arguments:

        - user_id: the ID of the user who owns the post.
        - post_id: the ID of the post to be deleted.

        """

        with db.get_session() as DB:
            Post.delete(DB, post_id)

        return "", 204  # No content.


def register(app, root, endpoint):
    """Add roots to an app at a specified root. Takes three parameters:

    - app: the app to which the routes should be added.
    - root: the URL root to use for all routes which are added.
    - endpoint: the name of the endpoint to be used for resolving URLs.

    """

    post_view = PostView.as_view(endpoint)

    app.add_url_rule(root, view_func=post_view, defaults={"post_id": None},
                     methods=["GET"])
    app.add_url_rule(root, view_func=post_view, methods=["POST"])
    app.add_url_rule("{0}/<int:post_id>".format(root), view_func=post_view,
                     methods=["GET", "PUT", "DELETE"])
