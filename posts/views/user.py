
import re

from flask import request
from flask.json import jsonify, loads
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from .. import db
from ..models import User

from .base import HandleErrorMixin


class UserView(MethodView, HandleErrorMixin):
    """Logic for various endpoints related to users."""

    def get(self, user_id):
        """Retrieve a single user or every user from the database, depending on
        whether or not user_id is None. Takes one argument:

        - user_id: the ID of the user to be retrived, or None for all users.

        """

        response = None

        if user_id is not None:
            try:
                with db.get_session() as DB:
                    user = DB.query(User).filter(User.id == user_id).one()
            except NoResultFound:
                return self.error("No user was found.", 404)

            response = user.to_dict()
            # response["links"] = self.get_actions(user)
        else:
            with db.get_session() as DB:
                users = DB.query(User).all()
            response = [u.to_dict() for u in users]

        return jsonify(response)

    def post(self):
        """Add a user to the database based on the information provided in the
        request."""

        if not request.data:
            return self.error("No data was provided.", 400)

        data = loads(request.data)

        name = data.get("name", "")
        email = data.get("email", "")

        if not name:
            return self.error("No name was provided.", 400)

        if not email:
            return self.error("No email was provided.", 400)

        # Very basic sanity check for a valid email.
        # (something without @)@(something without @).(something without @)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return self.error("An invalid email was provided.", 400)

        u = User(name=name, email=email)

        with db.get_session() as DB:
            DB.add(u)

        r = jsonify(u.to_dict())
        r.status_code = 201
        return r

    def put(self, user_id):
        """Update a user in the database based on the data in the request.
        Takes one argument:

        - user_id: the ID of the user to be updated.

        """

        if not request.data:
            return self.error("No data was provided.", 400)

        data = loads(request.data)

        name = data.get("name", "")
        email = data.get("email", "")

        if not name and not email:
            return self.error("No data was provided.", 400)

        updates = {}
        if name:
            updates[User.name] = name
        if email:
            updates[User.email] = email

        try:
            with db.get_session() as DB:
                DB.query(User).filter(User.id == user_id).update(updates)
                user = DB.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            return self.error("No user was found.", 404)

        return jsonify(user.to_dict())

    def delete(self, user_id):
        """Removes a user in the database. Takes one argument:

        - user_id: the ID of the user to be deleted.

        """

        with db.get_session() as DB:
            DB.query(User).filter(User.id == user_id).delete()

        return "", 204  # No content


def register(app, root, endpoint):
    """Add roots to an app at a specified root. Takes three parameters:

    - app: the app to which the routes should be added.
    - root: the URL root to use for all routes which are added.
    - endpoint: the name of the endpoint to be used for resolving URLs.

    """

    user_view = UserView.as_view(endpoint)

    app.add_url_rule(root, view_func=user_view, defaults={"user_id": None},
                     methods=["GET"], endpoint="{0}.list".format(endpoint))
    app.add_url_rule(root, view_func=user_view, methods=["POST"],
                     endpoint="{0}.create".format(endpoint))
    app.add_url_rule("{0}/<int:user_id>".format(root), view_func=user_view,
                     methods=["GET"], endpoint="{0}.view".format(endpoint))
    app.add_url_rule("{0}/<int:user_id>".format(root), view_func=user_view,
                     methods=["PUT"], endpoint="{0}.update".format(endpoint))
    app.add_url_rule("{0}/<int:user_id>".format(root), view_func=user_view,
                     methods=["DELETE"],
                     endpoint="{0}.delete".format(endpoint))
