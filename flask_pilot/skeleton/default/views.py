"""
Flask-Pilot views
"""

from flask import abort, request, redirect, url_for, jsonify
from flask_pilot import Pilot, route, flash_error, flash_success


class Index(Pilot):
    route_base = "/"

    def index(self):
        self.__(page_title="Hello Flask Pilot!")
        return self.render()

class Example(Pilot):
    def index(self):
        self.__(page_title="Example Page")
        flash_error("This is an error message set by flash_error() and called with show_flashed_message()")
        flash_success("This is a success message set by flash_error() and called with show_flashed_message()")
        return self.render()

class Error(Pilot):
    """
    Error Views
    """
    @classmethod
    def register(cls, app, **kwargs):
        super(cls, cls).register(app, **kwargs)

        # Bind the error to app
        @app.errorhandler(400)
        def error_400(error):
            return cls.index(error, 400)

        # Bind the error to app
        @app.errorhandler(401)
        def error_401(error):
            return cls.index(error, 401)

        @app.errorhandler(403)
        def error_403(error):
            return cls.index(error, 403)

        @app.errorhandler(404)
        def error_404(error):
            return cls.index(error, 404)

        @app.errorhandler(500)
        def error_500(error):
            return cls.index(error, 500)

        @app.errorhandler(503)
        def error_503(error):
            return cls.index(error, 503)

    @classmethod
    def index(cls, error, code):
        cls._(page_title="Error %s" % code)
        return cls.render(error=error), code
