"""
Pylot

"""

import os
import datetime
import inspect
from werkzeug.contrib.fixers import ProxyFix
from flask_classy import (FlaskView,
                          route)
from flask import (Flask,
                   abort,
                   redirect,
                   request,
                   render_template,
                   flash,
                   url_for,
                   jsonify,
                   session)

from flask_assets import Environment
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import utils

# ------------------------------------------------------------------------------
import pkginfo
NAME = pkginfo.NAME
__version__ = pkginfo.VERSION
__author__ = pkginfo.AUTHOR
__license__ = pkginfo.LICENSE
__copyright__ = pkginfo.COPYRIGHT

# ------------------------------------------------------------------------------

class Pylot(FlaskView):
    """
    Pylot a FlaskView extension
    """
    LAYOUT = "layout.html"  # The default layout
    assets = None
    _app = None
    _bind = set()
    _context = dict(
        APP_NAME="",
        APP_VERSION="",
        YEAR=datetime.datetime.now().year,
        GOOGLE_ANALYTICS_ID=None,
        LOGIN_ENABLED=False,
        LOGIN_OAUTH_ENABLED=False,
        LOGIN_OAUTH_CLIENT_IDS=[],
        LOGIN_OAUTH_BUTTONS=[],
        META=dict(
            title="",
            description="",
            url="",
            image="",
            site_name="",
            object_type="",
            locale="",
            keywords=[],
            use_opengraph=True,
            use_googleplus=True,
            use_twitter=True
        )
    )

    @classmethod
    def init(cls, flask_or_import_name, directory=None, config=None):
        """
        Allow to register all subclasses of Pylot
        So we call it once initiating
        :param flask_or_import_name: Flask instance or import name -> __name__
        :param directory: The directory containing your project's Views, Templates and Static
        :param config: string of config object. ie: "app.config.Dev"
        """
        if isinstance(flask_or_import_name, Flask):
            app = flask_or_import_name
        else:
            app = Flask(flask_or_import_name)

        app.wsgi_app = ProxyFix(app.wsgi_app)

        if config:
            app.config.from_object(config)

        if directory:
            app.template_folder = directory + "/templates"
            app.static_folder = directory + "/static"

        cls._app = app
        cls.assets = Environment(cls._app)

        for _app in cls._bind:
            _app(cls._app)

        for subcls in cls.__subclasses__():
            subcls.register(cls._app)

        return cls._app

    @classmethod
    def bind_(cls, kls):
        """
        To bind application that needs the 'app' object to init
        :param app: callable function that will receive 'Flask.app' as first arg
        """
        if not hasattr(kls, "__call__"):
            raise TypeError("From Pylot.bind_: '%s' is not callable" % kls)
        cls._bind.add(kls)
        return kls

    @classmethod
    def extends_(cls, kls):
        """
        A view decorator to extend another view class or function to itself
        It will inherit all its methods and propeties and use them on itself

        -- EXAMPLES --

        class Index(Pylot):
            pass

        index = Index()

        ::-> As decorator on classes ::
        @index.extends_
        class A(object):
            def hello(self):
                pass

        @index.extends_
        class C()
            def world(self):
                pass

        ::-> Decorator With function call ::
        @index.extends_
        def hello(self):
            pass

        """
        if inspect.isclass(kls):
            for _name, _val in kls.__dict__.items():
                if not _name.startswith("__"):
                    setattr(cls, _name, _val)
        elif inspect.isfunction(kls):
            setattr(cls, kls.__name__, kls)
        return cls

    @classmethod
    def context_(cls, **kwargs):
        """
        Assign a global view context to be used in the template
        :params **kwargs:
        """
        cls._context.update(kwargs)

    @classmethod
    def config_(cls, key, default=None):
        """
        Shortcut to access the config in your class
        :param key: The key to access
        :param default: The default value when None
        :returns mixed:
        """
        return cls._app.config.get(key, default)

    @classmethod
    def meta_(cls, **kwargs):
        """
        Meta allows you to add meta data to site
        :params **kwargs:

        meta keys we're expecting:
            title (str)
            description (str)
            url (str) (Will pick it up by itself if not set)
            image (str)
            site_name (str) (but can pick it up from config file)
            object_type (str)
            keywords (list)
            locale (str)

            **Boolean By default these keys are True
            use_opengraph
            use_twitter
            use_googleplus

        """
        _name_ = "META"
        meta_data = cls._context.get(_name_, {})
        for k, v in kwargs.items():
            # Prepend/Append string
            if (k.endswith("__prepend") or k.endswith("__append")) \
                    and isinstance(v, str):
                k, position = k.split("__", 2)
                _v = meta_data.get(k, "")
                if position == "prepend":
                    v += _v
                elif position == "append":
                    v = _v + v
            if k == "keywords" and not isinstance(k, list):
                raise ValueError("Meta keyword must be a list")
            meta_data[k] = v
        cls.context_(_name_=meta_data)

    @classmethod
    def success_(cls, message):
        """
        Set a flash success message
        """
        flash(message, "success")

    @classmethod
    def error_(cls, message):
        """
        Set a flash error message
        """
        flash(message, "error")

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

        data = data if data else dict()
        data["__"] = cls._context if cls._context else {}
        if kwargs:
            data.update(kwargs)

        data["__view_template__"] = view_template

        return render_template(layout or cls.LAYOUT, **data)




class Mailer(object):
    """
    A simple wrapper to switch between SES-Mailer and Flask-Mail based on config
    """
    mail = None
    provider = None

    def init_app(self, app):
        import ses_mailer
        import flask_mail

        self.app = app
        self.provider = app.config.get("MAILER_BACKEND", "SES").upper()
        if self.provider not in ["SES", "FLASK-MAIL"]:
            raise AttributeError("Invalid Mail provider")

        if self.provider == "SES":
            self.mail = ses_mailer.Mail(app=app)
        elif self.provider == "FLASK-MAIL":
            self.mail = flask_mail.Mail(app)

    def send(self, to, subject, body, reply_to=None, **kwargs):
        """
        Send simple message
        """
        if self.provider == "SES":
            self.mail.send(to=to,
                           subject=subject,
                           body=body,
                           reply_to=reply_to,
                           **kwargs)
        elif self.provider == "FLASK-MAIL":
            msg = flask_mail.Message(recipients=to, subject=subject, body=body, reply_to=reply_to,
                                     sender=self.app.config.get("MAIL_DEFAULT_SENDER"))
            self.mail.send(msg)

    def send_template(self, template, to, reply_to=None, **context):
        """
        Send Template message
        """
        if self.provider == "SES":
            self.mail.send_template(template=template, to=to, reply_to=reply_to, **context)
        elif self.provider == "FLASK-MAIL":
            ses_mail = ses_mailer.Mail(app=self.app)
            data = ses_mail.parse_template(template=template, **context)

            msg = flask_mail.Message(recipients=to,
                                     subject=data["subject"],
                                     body=data["body"],
                                     reply_to=reply_to,
                                     sender=self.app.config.get("MAIL_DEFAULT_SENDER")
                                     )
            self.mail.send(msg)


class Storage(object):

    store = None
    def init_app(self, app):
        import flask_store

        type = app.config.get("STORAGE_BACKEND", "LOCAL")
        if type == "S3":
            provider = "flask_store.providers.s3.S3Provider"
        elif type == "LOCAL":
            provider = "flask_store.providers.local.LocalProvider"
        else:
            provider = app.config.get("STORAGE_BACKEND")

        bucket = app.config.get("STORAGE_S3_BUCKET", "")
        domain = app.config.get("STORAGE_DOMAIN", "https://s3.amazonaws.com/%s/" % bucket)
        app.config.update({
            "STORE_PROVIDER": provider,
            "STORE_PATH": app.config.get("STORAGE_PATH"),
            "STORE_URL_PREFIX": app.config.get("STORAGE_URL_PREFIX", "files"),
            "STORE_DOMAIN": domain,
            "STORE_S3_REGION": app.config.get("STORAGE_S3_REGION", "us-east-1"),
            "STORE_S3_BUCKET": bucket,
            "STORE_S3_ACCESS_KEY": app.config.get("AWS_ACCESS_KEY_ID"),
            "STORE_S3_SECRET_KEY": app.config.get("AWS_SECRET_ACCESS_KEY")
        })
        self.store = flask_store.Store(app=app)

    def get_url(self, file, absolute=False):
        provider = self.store.Provider(file)
        return provider.absolute_url if absolute else provider.relative_url

    def get_path(self, file, absolute=False):
        provider = self.store.Provider(file)
        return provider.absolute_path if absolute else provider.relative_path

    def get(self):
        pass

    def put(self, file):
        provider = self.store.Provider(file)
        provider.save()
        return dict(filename=provider.filename,
                    relative_url=provider.relative_url,
                    absolute_url=provider.absolute_url,
                    absolute_path=provider.absolute_path)

    def exists(self, file):
        provider = self.store.Provider(file)
        return provider.exists()


class Cache(object):
    pass


class Session(object):
    def __init__(self, app):
        self.app = app

        # SESSION
        store = None
        backend = self.app.config.get("SESSION_BACKEND")
        if backend:
            backend = backend.upper()
            if backend == "REDIS":
                uri = self.app.config.get("SESSION_BACKEND_URI")
                _redis = utils.connect_redis(uri)
                store = RedisStore(_redis)
        if store:
            KVSessionExtension(store, self.app)


class AppError(Exception):
    """ For exception in application pages """
    pass

# ------------------------------------------------------------------------------


# Setup facade

mailer = Mailer()
storage = Storage()
cache = Cache()

Pylot.bind_(Session)
Pylot.bind_(mailer.init_app)
Pylot.bind_(storage.init_app)
