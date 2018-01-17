
from flask.json import jsonify
from flask.views import MethodView

from .. import db
from ..models import User


class UserView(MethodView):
    def get(self, user_id):
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


def register(app, root, endpoint):
    user_view = UserView.as_view(endpoint)
    app.add_url_rule(root, view_func=user_view, defaults={"user_id": None},
                     methods=["GET"])
    app.add_url_rule("{0}/<int:user_id>".format(root), view_func=user_view,
                     methods=["GET"])
