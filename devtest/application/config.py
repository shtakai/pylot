"""
::PYLOT::

Base config file

"""
from pylot import utils

class Config(object):
    """
    Flask config: http://flask.pocoo.org/docs/0.10/config/
    """
    SERVER_NAME = None
    DEBUG = True
    SECRET_KEY = "PLEASE CHANGE ME"

    # ------

    APP_NAME = ""
    APP_VERSION = "0.0.1"

    #
    ADMIN_EMAIL = "admin@test.com"
    ADMIN_NAME = "Admin Test"

    # AWS Credentials
    # For: S3, SES Mailer, flask s3
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
    AWS_S3_BUCKET_NAME = "yoredis"

# ------- DATABASES ------------

    # SQLAlchemy
    DATABASE_URI = "" #"sqlite://///Users/mardochee.macxis/Projects/Python/flask-pilot/test/app.db"

    # REDIS
    REDIS_URI = None

# -----------------------------
    # SESSION
    #

    #: SESSION_BACKEND. Default: None. Optional: REDIS
    SESSION_BACKEND = None

    #: SESSION_BACKEND_URI
    SESSION_BACKEND_URI = REDIS_URI


    # CACHE
    #:
    CACHE_BACKEND = None

    CACHE_BACKEND_URI = ""
# -----------------
    # WEBASSETS

    # Flask-Assets
    # http://flask-assets.readthedocs.org/
    ASSETS_DEBUG = False
    FLASK_ASSETS_USE_S3 = False

    # Flask-S3
    # https://flask-s3.readthedocs.org/en/v0.1.4/
    USE_S3 = False
    S3_BUCKET_DOMAIN = ""
    S3_BUCKET_NAME = AWS_S3_BUCKET_NAME
    S3_USE_HTTPS = False
    USE_S3_DEBUG = False
    S3_ONLY_MODIFIED = False

# ----------------------------------
    # STORAGE
    # Allows you to store uploaded files on local system or in the cloud

    #: STORAGE_PROVIDER: The provider to use.
    # By default it's 'LOCAL'. You can use 'S3'
    STORAGE_BACKEND = "S3"

    #: STORAGE_PATH: The path
    STORAGE_PATH = "application/var/uploads"

    #: STORAGE_URL_PREFIX
    STORAGE_URL_PREFIX = "files"

    #: STORAGE_S3_BUCKET
    STORAGE_S3_BUCKET = "yoredis"

    #: STORAGE_ALLOWED_EXTENSION
    STORAGE_ALLOWED_EXTENSION = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

# -------------------------------
    # MAILER
    # Let you send mail by using AWS SES or SMTP
    # You can send raw email, or templated email for convenience

    #: MAILER_PROVIDER - 'SES' or SMTP
    MAILER_BACKEND = "SES"  # SES | SMTP

    #: MAILER_SENDER - The sender of the email by default
    # For SES, this email must be authorized
    MAILER_SENDER = ""

    #: MAILER_REPLY_TO: The email to reply to by default
    MAILER_REPLY_TO = ""

    #: MAILER_TEMPLATE: a directory that contains the email template or a dict
    #
    MAILER_TEMPLATE = ""

    #: MAILER_SMTP_URI: The uri for the smtp connection
    # format: USERNAME:PASSWORD@HOST:PORT
    MAILER_SMTP_URI = "" # user:password@host:port

    # SES MAILER
    # https://github.com/mardix/ses-mailer
    SES_SENDER = "mcx2082@gmail.com"
    SES_REPLY_TO = ""
    SES_TEMPLATE = "%s/devtest/application/var/ses-mailer" % utils.get_base_dir()
    SES_TEMPLATE_CONTEXT = {
        "site_name": "MyTestSite.com",
        "site_url": "http://mytestsite.com"
    }

    # Flask Mailer
    # https://pythonhosted.org/Flask-Mail/
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = None

# ------------------------------------

    # Flask-ReCaptcha
    # https://github.com/mardix/flask-recaptcha
    RECAPTCHA_SITE_KEY = ""
    RECAPTCHA_SECRET_KEY = ""

    # Google Analytics
    GOOGLE_ANALYTICS_ID = ""

# ----- LOGIN -----


    LOGIN_RESET_PASSWORD_DELIVERY = "TOKEN"  # PASSWORD | TOKEN

    LOGIN_EMAIL_ENABLE = True
    LOGIN_OAUTH_ENABLE = True
    LOGIN_SIGNUP_ENABLE = True
    LOGIN_OAUTH_CREDENTIALS = {
        "FACEBOOK": {
            "ENABLE": True,
            "CLIENT_ID": ""
        },
        "GOOGLE": {
            "ENABLE": True,
            "CLIENT_ID": ""
        },
        "TWITTER": {
            "ENABLE": False,
            "CLIENT_ID": ""
        }
    }

    # Maintenance
    # Turn maintenance page ON and OFF
    MAINTENANCE_ON = False


    # Contact
    # Email address for the contact page receipient
    CONTACT_PAGE_EMAIL_RECIPIENT = ""


class Development(Config):
    pass


class Production(Config):
    SECRET_KEY = None
