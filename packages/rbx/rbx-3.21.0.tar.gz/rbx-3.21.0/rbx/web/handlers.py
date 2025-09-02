import os

from flask import jsonify, request
from google.cloud.error_reporting import Client
from google.cloud.error_reporting.util import build_flask_context

from ..exceptions import BadRequest, TransientException


def register_error_handlers(app):
    """Register handlers for Exceptions.

    Any exception, whether raised manually or unexpected, will be caught and returned as a
    JSON-formatted response.

    We catch any code-specific Exceptions, namely custom validation (400) and uncaught
    errors (500).

    Custom validation should be raised in the app using the BadRequest class:

    >>> raise BadRequest('Message')

    """

    @app.errorhandler(401)
    def unauthorized(error):
        response = jsonify(message="Unauthorized")
        response.status_code = 401
        return response

    @app.errorhandler(403)
    def forbidden(error):
        response = jsonify(message="Forbidden")
        response.status_code = 403
        return response

    @app.errorhandler(404)
    def not_found(error):
        response = jsonify(message="Not Found")
        response.status_code = 404
        return response

    @app.errorhandler(405)
    def method_not_allowed(error):
        response = jsonify(message="Method Not Allowed")
        response.status_code = 405
        return response

    @app.errorhandler(408)
    def request_timeout(error):
        response = jsonify(message="Request Timeout")
        response.status_code = 408
        return response

    @app.errorhandler(415)
    def unsupported_media_type(error):
        response = jsonify(message="Unsupported Media Type")
        response.status_code = 415
        return response

    @app.errorhandler(429)
    def too_many_requests(error):
        response = jsonify(message="Too Many Requests")
        response.status_code = 429
        return response

    # BadRequest exceptions
    @app.errorhandler(BadRequest)
    def invalid_exception(error):
        app.logger.debug(error.to_dict())
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # TransientException exceptions
    @app.errorhandler(TransientException)
    def transient_exception(error):
        response = jsonify(message="Request Timeout")
        response.status_code = 408
        return response

    # Uncaught exceptions
    @app.errorhandler(Exception)
    def unhandled_exception(error):
        if os.getenv("GAE_ENV", "").startswith("standard"):
            client = Client()
            client.report_exception(http_context=build_flask_context(request))
        else:
            app.logger.exception(f"Unhandled Exception: {error}")

        response = jsonify(
            message="Something went wrong!",
            details=[
                "You have experienced a technical error.",
                "We are working to correct this issue.",
                "Please wait a few moments and try again.",
            ],
        )
        response.status_code = 500
        return response
