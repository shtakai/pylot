"""
Flask-Pilot

"""

import os
from flask import render_template, request, flash, get_flashed_messages
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.classy import FlaskView, route  # flask-classy
from flask.ext.assets import Environment  # flask-assets
import inspect

# ------------------------------------------------------------------------------
NAME = "Flask-Pilot"
__version__ = "0.1.0"
__author__ = "Mardix"
__license__ = "MIT"
__copyright__ = "(c) 2014 Mardix"

# ------------------------------------------------------------------------------

# Flash Messages: error, success, info
def flash_error(message):
    """
    Set an `error` flash message
    :param message: string - The message
    """
    flash(message, "error")


def flash_success(message):
    """
    Set a `success` flash message
    :param message: string - The message
    """
    flash(message, "success")


def flash_info(message):
    """
    Set an `info` flash message
    :param message: string - The message
    """
    flash(message, "info")


# COOKIES: set, get, delete
def set_cookie(key, value="", **kwargs):
    """
    Set a cookie

    :param key: the key (name) of the cookie to be set.
    :param value: the value of the cookie.
    :param max_age: should be a number of seconds, or `None` (default) if
                    the cookie should last only as long as the client's
                    browser session.
    :param expires: should be a `datetime` object or UNIX timestamp.
    :param domain: if you want to set a cross-domain cookie.  For example,
                   ``domain=".example.com"`` will set a cookie that is
                   readable by the domain ``www.example.com``,
                   ``foo.example.com`` etc.  Otherwise, a cookie will only
                   be readable by the domain that set it.
    :param path: limits the cookie to a given path, per default it will
                 span the whole domain.
    """
    kwargs.update({"key": key, "value": value})
    Pilot._set_cookie_ = kwargs


def get_cookie(key):
    """
    Get cookie
    """
    return request.cookies.get(key)


def del_cookie(key, path='/', domain=None):
    """
    Delete a cookie.  Fails silently if key doesn't exist.

    :param key: the key (name) of the cookie to be deleted.
    :param path: if the cookie that should be deleted was limited to a
                 path, the path has to be defined here.
    :param domain: if the cookie that should be deleted was limited to a
                   domain, that domain has to be defined here.
    """
    set_cookie(key=key, value='', expires=0, max_age=0, path=path, domain=domain)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class Pilot(FlaskView):
    """
    Pilot a FlaskView extension
    """
    LAYOUT = "layout.html"  # The default layout
    assets = None
    _app = None
    _bind_app = set()
    _set_cookie_ = None
    _view_context = dict()
    _UTILITY_PAGE_INFO = dict()

    @classmethod
    def bind(cls, app):
        """
        To bind application that needs the 'app' object to init
        :param app: callable function that will receive 'Flask.app' as first arg
        """
        if not hasattr(app, "__call__"):
            raise TypeError("From Pilot.bind: '%s' is not callable" % app)
        cls._bind_app.add(app)

    @classmethod
    def init(cls, app, config=None, project_dir=None, proxyfix=True):
        """
        Allow to register all subclasses of Pilot
        So we call it once initiating
        :param app: The app
        :param config: string of config object. ie: "app.config.Dev"
        :param project_dir: The directory containing your project's Views, Templates and Static
        :param proxyfix:
        """

        if not project_dir:
            project_dir = os.getcwd()

        if config:
            app.config.from_object(config)

        if proxyfix:
            app.wsgi_app = ProxyFix(app.wsgi_app)

        cls._app = app
        cls.assets = Environment(app)

        app.template_folder = project_dir + "/templates"
        app.static_folder = project_dir + "/static"

        for _app in cls._bind_app:
            _app(app)

        for subcls in cls.__subclasses__():
            subcls.register(app)

        @app.after_request
        def after_request(response):
            # Set the cookie on response
            if cls._set_cookie_:
                response.set_cookie(**cls._set_cookie_)
            return response

        return app

    @classmethod
    def get_config(cls, key, default=None):
        """
        Shortcut to access the config in your class
        :param key: The key to access
        :param default: The edfault value when None
        :returns mixed:
        """
        return cls._app.config.get(key, default)

    @classmethod
    def _(cls, **kwargs):
        """
        Set view context to be available in the whole context
        It usually set a specific context once
        :params **kwargs:
        """
        cls._view_context.update(kwargs)

    @classmethod
    def render(cls, data={}, view_template=None, layout=None, **kwargs):
        """
        To render data to the associate template file of the action view
        :param data: The context data to pass to the template
        :param view_template: The file template to use. By default it will map the classname/action.html
        :param layout: The body layout, must contain {% include __view_template__ %}
        """
        if not view_template:
            stack = inspect.stack()[1]
            module = inspect.getmodule(cls).__name__
            module_name = module.split(".")[-1]
            action_name = stack[3]      # The method being called in the class
            view_name = cls.__name__    # The name of the class without View

            if view_name.endswith("View"):
                view_name = view_name[:-4]
            view_template = "%s/%s.html" % (view_name, action_name)

        if not data:
            data = dict()
        if cls._view_context:
            data["_"] = cls._view_context
        if kwargs:
            data.update(kwargs)

        data["__flashed_messages__"] = get_flashed_messages(with_categories=True)
        data["__view_template__"] = view_template

        return render_template(layout or cls.LAYOUT, **data)

