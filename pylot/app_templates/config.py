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

    #------

    APP_NAME = ""
    APP_VERSION = "0.0.1"

    #
    ADMIN_EMAIL = ""
    ADMIN_NAME = ""

    # AWS Credentials
    # For: S3, SES Mailer, flask s3
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
    AWS_S3_BUCKET_NAME = ""

    # SQLAlchemy
    DATABASE_URI = "sqlite://"

    # REDIS
    REDIS_URI = None

    # Session
    SESSION_BACKEND = None
    SESSION_BACKEND_URI = REDIS_URI

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

    # SES MAILER
    # https://github.com/mardix/ses-mailer
    SES_SENDER = ""
    SES_REPLY_TO = ""
    SES_TEMPLATE = "%s/application/var/ses-mailer" % utils.get_base_dir()
    SES_TEMPLATE_CONTEXT = {
        "site_name": "MyTestSite.com",
        "site_url": "http://mytestsite.com"
    }


    # Contact
    # Email address for the contact page receipient
    CONTACT_PAGE_EMAIL_RECIPIENT = "mcx2082@gmail.com"

    # Flask-ReCaptcha
    # https://github.com/mardix/flask-recaptcha
    RECAPTCHA_SITE_KEY = ""
    RECAPTCHA_SECRET_KEY = ""

    # Google Analytics
    GOOGLE_ANALYTICS_ID = ""

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


class Development(Config):
    pass


class Production(Config):
    SECRET_KEY = None
