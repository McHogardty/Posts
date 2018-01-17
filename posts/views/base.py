
from flask.json import jsonify


class HandleErrorMixin(object):
    """Contains logic for handling and responding to errors."""

    def error(self, message, status_code):
        """Return an error to the user. Takes two parameters:

        - message: the error message to be returned.
        - status_code: the HTTP status code for the response.

        """

        r = jsonify({"error": message})
        r.status_code = status_code
        return r
