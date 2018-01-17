
from flask import request
from flask.json import jsonify, loads
from flask.views import MethodView

from .. import db
from ..models import User


class UserView(MethodView):
    """Logic for various endpoints related to users."""

    def get(self, user_id):
        """Retrieve a single user or every user from the database, depending on
        whether or not user_id is None. Takes one argument:

        - user_id: the ID of the user to be retrived, or None for all users.

        """

        response = None

        if user_id is not None:
            with db.get_session() as DB:
                user = DB.query(User).filter(User.id == user_id).one()
            response = user.to_dict()
        else:
            with db.get_session() as DB:
                users = DB.query(User).all()
            response = [u.to_dict() for u in users]

        return jsonify(response)

    def post(self):
        """Add a user to the database based on the information provided in the
        request."""

        data = loads(request.data)

        name = data.get("name", "")
        email = data.get("email", "")

        u = User(name=name, email=email)

        with db.get_session() as DB:
            DB.add(u)

        r = jsonify(u.to_dict())
        r.status_code = 201
        return r


def register(app, root, endpoint):
    """Add roots to an app at a specified root. Takes three parameters:

    - app: the app to which the routes should be added.
    - root: the URL root to use for all routes which are added.
    - endpoint: the name of the endpoint to be used for resolving URLs.

    """

    user_view = UserView.as_view(endpoint)
    app.add_url_rule(root, view_func=user_view, defaults={"user_id": None},
                     methods=["GET"])
    app.add_url_rule(root, view_func=user_view, methods=["POST"])
    app.add_url_rule("{0}/<int:user_id>".format(root), view_func=user_view,
                     methods=["GET"])
