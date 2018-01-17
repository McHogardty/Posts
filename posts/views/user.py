
from flask.json import jsonify
from flask.views import MethodView

from .. import db
from ..models import User


class UserView(MethodView):
    def get(self):
        with db.get_session() as DB:
            users = DB.query(User).all()

        return jsonify([u.to_dict() for u in users])


def register(app, root, endpoint):
    user_view = UserView.as_view(endpoint)
    app.add_url_rule(root, view_func=user_view, methods=["GET"])
