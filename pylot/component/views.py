"""
Pylot views components
"""

import os
import datetime
from hashlib import sha1
import time
import base64
import hmac
import urllib
import pkg_resources
import functools
import re
from pylot import utils
import humanize
import mistune
import jinja2
from pylot import (Pylot,
                   mailer,
                   storage,
                   route,
                   abort,
                   redirect,
                   request,
                   url_for,
                   jsonify,
                   session)
from flask_recaptcha import ReCaptcha
from flask_login import (LoginManager,
                         login_required,
                         login_user,
                         logout_user,
                         current_user)
from flask_assets import (Environment, Bundle)


class _InitViews(object):
    def __init__(self, app):
        self.app = app
        self.register_templates()
        self.setup_config()

    def setup_config(self):
        if self.app.config.get("APP_NAME"):
            Pylot.context_(APP_NAME=self.app.config.get("APP_NAME"))
        if self.app.config.get("APP_VERSION"):
            Pylot.context_(APP_VERSION=self.app.config.get("APP_VERSION"))

        # OAUTH LOGIN
        if self.app.config.get("LOGIN_OAUTH_ENABLE"):
            _sl = self.app.config.get("LOGIN_OAUTH_CREDENTIALS")
            if _sl and isinstance(_sl, dict):
                client_ids = {}
                buttons = []
                for name, prop in _sl.items():
                    if isinstance(prop, dict):
                        if prop["ENABLE"]:
                            _name = name.lower()
                            client_ids[_name] = prop["CLIENT_ID"]
                            buttons.append(_name)

            Pylot.context_(LOGIN_OAUTH_ENABLED=True,
                     LOGIN_OAUTH_CLIENT_IDS=client_ids,
                     LOGIN_OAUTH_BUTTONS=buttons)


    def register_templates(self):
        # Register the templates
        path = pkg_resources.resource_filename(__name__, "templates")
        utils.add_path_to_jinja(self.app, path)

        # Register Assets
        _dir_ = os.path.dirname(__file__)
        env = Pylot.assets
        env.load_path = [
            Pylot._app.static_folder,
            os.path.join(_dir_, 'static'),
        ]

        env.register(
            'pylot_js',
            Bundle(
                "pylot/js/s3upload.js",
                "pylot/js/hello.js",
                "pylot/js/pylot.js",
                output='pylot.js'
            )
        )
        env.register(
            'pylot_css',
            Bundle(
                'pylot/css/pylot.css',
                'pylot/css/bootstrap-social-btns.css',
                output='pylot.css'
            )
        )
Pylot.bind_(_InitViews)


def with_user_roles(roles):
    """
    with_user_roles(roles)

    It allows to check if a user has access to a view by adding the decorator
    with_user_roles([])

    Requires flask-login

    In your model, you must have a property 'role', which will be invoked to
    be compared to the roles provided.

    If current_user doesn't have a role, it will throw a 403

    If the current_user is not logged in will throw a 401

    * Require Flask-Login
    ---
    Usage

    @app.route('/user')
    @login_require
    @with_user_roles(['admin', 'user'])
    def user_page(self):
        return "You've got permission to access this page."
    """
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.is_authenticated():
                if not hasattr(current_user, "role"):
                    raise AttributeError("<'role'> doesn't exist in login 'current_user'")
                if current_user.role not in roles:
                    return abort(403)
            else:
                return abort(401)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

recaptcha = ReCaptcha()
Pylot.bind_(recaptcha.init_app)

# ------------------------------------------------------------------------------

class StorageUploadView(object):

    def sign_s3_upload(self):
        """
        Allow to create Signed object to upload to S3 via JS
        """
        AWS_ACCESS_KEY = self.config_('AWS_ACCESS_KEY_ID')
        AWS_SECRET_KEY = self.config_('AWS_SECRET_ACCESS_KEY')
        S3_BUCKET = self.config_('AWS_S3_BUCKET_NAME')

        object_name = request.args.get('s3_object_name')
        mime_type = request.args.get('s3_object_type')
        expires = long(time.time()+10)
        amz_headers = "x-amz-acl:public-read"
        put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)
        signature = base64.encodestring(hmac.new(AWS_SECRET_KEY, put_request, sha1).digest())
        signature = urllib.quote(urllib.quote_plus(signature.strip()))
        url = 'https://s3.amazonaws.com/%s/%s' % (S3_BUCKET, object_name)
        return jsonify({
            'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
             'url': url
          })


    def upload_to_storage(self):
        pass


class MarkdownEditorView(object):
    def upload_mardown_editor_image(self):
        """
        Placeholder for markdown
        """

        # For when there is an error
        error = False
        if error:
            return "error message", 401

        return jsonify({
            "id": "",
            "url": "", # full image url
        })


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def login_view(model, **kwargs):

    def wrapper(view):

        Pylot.context_(COMPONENT_LOGIN=True)

        view_name = view.__name__

        User = model.UserStruct.User

        # Login
        login_view = "%s:login" % view_name
        on_signin_view = kwargs["on_signin_view"] if "on_signin_view" \
                                                     in kwargs else "Index:index"
        on_signout_view = kwargs["on_signout_view"] if "on_signout_view" \
                                                       in kwargs else "Index:index"
        template_dir = kwargs["template_dir"] if "template_dir" \
                                                 in kwargs else "Pylot/Login"
        template_page = template_dir + "/%s.html"


        login_manager = LoginManager()
        login_manager.login_view = login_view
        login_manager.login_message_category = "error"
        Pylot.bind_(login_manager.init_app)
        @login_manager.user_loader
        def load_user(userid):
            return User.get(userid)

        @view.extends_
        class Login_(object):
            #route_base = "/"

            SESSION_KEY_SET_EMAIL_DATA = "set_email_tmp_data"

            @classmethod
            def signup_handler(cls):
                """
                To handle the signup process. Must still bind to the app
                 :returns User object:
                """
                if request.method == "POST":
                    name = request.form.get("name")
                    email = request.form.get("email")
                    password = request.form.get("password")
                    password2 = request.form.get("password2")
                    profile_pic_url = request.form.get("profile_pic_url", None)

                    if not name:
                        raise UserWarning("Name is required")
                    elif not utils.is_valid_email(email):
                        raise UserWarning("Invalid email address '%s'" % email)
                    elif not password.strip() or password.strip() != password2.strip():
                        raise UserWarning("Passwords don't match")
                    elif not utils.is_valid_password(password):
                        raise UserWarning("Invalid password")
                    else:
                        return User.new(email=email,
                                        password=password.strip(),
                                        name=name,
                                        profile_pic_url=profile_pic_url,
                                        signup_method="EMAIL")

            @classmethod
            def change_login_handler(cls, user_context=None, email=None):
                if not user_context:
                    user_context = current_user
                if not email:
                    email = request.form.get("email").strip()

                if not utils.is_valid_email(email):
                    raise UserWarning("Invalid email address '%s'" % email)
                else:
                    if email != user_context.email and User.get_by_email(email):
                        raise UserWarning("Email exists already '%s'" % email)
                    elif email != user_context.email:
                        user_context.update(email=email)
                        return True
                return False

            @classmethod
            def change_password_handler(cls, user_context=None, password=None,
                                        password2=None):
                if not user_context:
                    user_context = current_user
                if not password:
                    password = request.form.get("password").strip()
                if not password2:
                    password2 = request.form.get("password2").strip()

                if password:
                    if password != password2:
                        raise UserWarning("Password don't match")
                    elif not utils.is_valid_password(password):
                        raise UserWarning("Invalid password")
                    else:
                        user_context.set_password(password)
                        return True
                else:
                    raise UserWarning("Password is empty")

            @classmethod
            def reset_password_handler(cls, user_context=None,
                                       delivery=None,
                                       send_notification=True):
                """
                Reset the password
                :returns string: The new password string
                """
                if not user_context:
                    user_context = current_user

                if delivery.upper() == "TOKEN":
                    token = user_context.set_reset_password_token()
                    if send_notification:
                        url = url_for("%s:reset_password_token" % view_name,
                                      token=token,
                                      _external=True)
                        mailer.send_template("reset-password-token.txt",
                                             to=user_context.email,
                                             name=user_context.name,
                                             reset_password_url=url
                                             )
                    return token
                else:
                    new_password = user_context.set_random_password()
                    if send_notification:
                        url = url_for(login_manager.login_view, _external=True)
                        mailer.send_template("reset-password.txt",
                                             to=user_context.email,
                                             new_password=new_password,
                                             name=user_context.name,
                                             login_url=url
                                             )

            def _can_login(self):
                if not self.config_("LOGIN_EMAIL_ENABLE"):
                    abort(403)

            def _can_oauth_login(self):
                if not self.config_("LOGIN_OAUTH_ENABLE"):
                    abort(403)

            def _can_signup(self):
                if not self.config_("LOGIN_SIGNUP_ENABLE"):
                    abort(403)

            def _login_user(self, user_context):
                login_user(user_context)
                user_context.update_last_login()
                user_context.update_last_visited()

            # --- LOGIN
            def login(self):
                """
                Login page
                """
                self._can_login()
                logout_user()
                self.meta_(title="Login")
                return self.render(login_url_next=request.args.get("next", ""),
                                   view_template=template_page % "login")

            @route("email-login", methods=["POST"])
            def email_login(self):
                """
                login via email
                """
                self._can_login()

                email = request.form.get("email").strip()
                password = request.form.get("password").strip()

                if not email or not password:
                    self.error_("Email or Password is empty")
                    return redirect(url_for(login_view, next=request.form.get("next")))
                account = User.get_by_email(email)
                if account and account.password_matched(password):
                    self._login_user(account)
                    return redirect(request.form.get("next") or url_for(on_signin_view))
                else:
                    self.error_("Email or Password is invalid")
                    return redirect(url_for(login_view, next=request.form.get("next")))

            # OAUTH Login
            @route("oauth-login", methods=["POST"])
            def oauth_login(self):
                """
                To login via social
                """
                self._can_oauth_login()

                email = request.form.get("email").strip()
                name = request.form.get("name").strip()
                provider = request.form.get("provider").strip()
                provider_user_id = request.form.get("provider_user_id").strip()
                image_url = request.form.get("image_url").strip()
                next = request.form.get("next", "")
                # save to session and redirect to enter email address
                if not email:
                    session[self.SESSION_KEY_SET_EMAIL_DATA] = {
                        "type": "social_login",
                        "email": email,
                        "name": name,
                        "provider": provider,
                        "provider_user_id": provider_user_id,
                        "image_url": image_url,
                        "next": next,
                        "signup_method": "SOCIAL:%s" % provider.upper()
                    }
                    return redirect(url_for("Login:set_email", next=request.form.get("next", "")))
                else:
                    user = User.oauth_register(provider=provider,
                                               provider_user_id=provider_user_id,
                                               email=email,
                                               name=name,
                                               image_url=image_url,
                                               signup_method="SOCIAL:%s" % provider.upper())
                    if user:
                        self._login_user(user)
                        return redirect(request.form.get("next") or url_for(on_signin_view))

                return redirect(url_for(login_view, next=request.form.get("next", "")))

            # OAUTH Login
            @route("oauth-connect", methods=["POST"])
            @login_required
            def oauth_connect(self):
                """
                To login via social
                """
                email = request.form.get("email").strip()
                name = request.form.get("name").strip()
                provider = request.form.get("provider").strip()
                provider_user_id = request.form.get("provider_user_id").strip()
                image_url = request.form.get("image_url").strip()
                next = request.form.get("next", "")
                try:
                    current_user.oauth_connect(provider=provider,
                                             provider_user_id=provider_user_id,
                                             email=email,
                                             name=name,
                                             image_url=image_url)
                except Exception as ex:
                    self.error_("Unable to link your account")

                return redirect(url_for("%s:account_settings" % view_name))

            # --- LOGOUT
            def logout(self):
                logout_user()
                self.success_("Logout successfully!")
                return redirect(url_for(on_signout_view or login_view))

            # --- LOST PASSWORD
            @route("lost-password", methods=["GET", "POST"])
            def lost_password(self):
                self._can_login()
                self.meta_(title="Lost Password")
                if request.method == "POST":
                    email = request.form.get("email")
                    user = User.get_by_email(email)
                    if user:
                        delivery = self.config_("LOGIN_RESET_PASSWORD_DELIVERY")
                        self.reset_password_handler(user_context=user, delivery=delivery)
                        self.success_("A new password has been sent to '%s'" % email)
                    else:
                        self.error_("Invalid email address")
                    return redirect(url_for(login_view))
                else:
                    logout_user()
                    return self.render(view_template=template_page % "lost_password")

            @route("set-email", methods=["GET", "POST"])
            @login_required
            def set_email(self):
                self._can_login()
                self.meta_(title="Set Email")

                # Only user without email can set email
                if current_user.email:
                    return redirect(url_for("%s:account_settings" % view_name))

                if request.method == "POST":
                    email = request.form.get("email")
                    if not utils.is_valid_email(email):
                        self.error_("Invalid email address '%s'" % email)
                        return redirect(url_for(login_view))

                    if email and self.SESSION_KEY_SET_EMAIL_DATA in session:
                        _data = session[self.SESSION_KEY_SET_EMAIL_DATA]
                        user = User.get_by_email(email)
                        if user:
                            self.error_("An account is already using '%s'" % email)
                        else:
                            User.new(email=email,
                                     name=_data["name"],
                                     signup_method=_data["signup_method"] if "signup_method" in _data else "" )

                            if "type" in _data:
                                if _data["type"] == "social_login":
                                    user = User.social_login(provider=_data["provider"],
                                                             provider_user_id=_data["provider_user_id"],
                                                             email=email,
                                                             name=_data["name"],
                                                             image_url=_data["image_url"])
                                    return redirect(request.form.get("next") or url_for(on_signin_view))

                        return redirect(url_for("%s:set_email" % view_name,
                                                next=request.form.get("next", "")))
                else:
                    return self.render(view_template=template_page % "set_email")

            # --- RESET PASSWORD
            @route("reset-password-token/<token>")
            def reset_password_token(self, token):
                self._can_login()
                user = User.get_by_token(token)
                if not user:
                    self.error_("Invalid reset password token. Please try again")
                    return redirect(url_for("%s:lost_password" % view_name))
                else:
                    self._login_user(user)
                    return redirect(url_for("%s:reset_password" % view_name))

            @route("reset-password", methods=["GET", "POST"])
            @login_required
            def reset_password(self):
                self._can_login()
                self.meta_(title="Reset Password")
                if current_user.require_password_change:
                    if request.method == "POST":
                        try:
                            self.change_password_handler()
                            current_user.clear_reset_password_token()
                            self.success_("Password updated successfully!")
                            return redirect(url_for(on_signin_view))
                        except Exception as ex:
                            self.error_("Error: %s" % ex.message)
                            return redirect(url_for("%s:reset_password" % view_name))
                    return self.render(view_template=template_page % "reset_password")
                return redirect(url_for(on_signin_view))

            # --
            @route("signup", methods=["GET", "POST"])
            def signup(self):
                self._can_login()
                self._can_signup()
                self.meta_(title="Signup")
                if request.method == "POST":
                    # reCaptcha
                    if not recaptcha.verify():
                        self.error_("Invalid Security code")
                        return redirect(url_for("Login:signup", next=request.form.get("next")))
                    try:
                        new_account = self.signup_handler()
                        login_user(new_account)
                        self.success_("Congratulations! ")
                        return redirect(request.form.get("next") or url_for(on_signin_view))
                    except Exception as ex:
                        self.error_(ex.message)
                    return redirect(url_for("%s:signup" % view_name, next=request.form.get("next")))

                logout_user()
                return self.render(login_url_next=request.args.get("next", ""),
                                   view_template=template_page % "signup")

            # --------

            @route("/account-settings")
            @login_required
            def account_settings(self):
                self.meta_(title="Account Settings")
                return self.render(view_template=template_page % "account_settings")

            @route("/change-login", methods=["POST"])
            @login_required
            def change_login(self):
                confirm_password = request.form.get("confirm-password").strip()
                try:
                    if current_user.password_matched(confirm_password):
                        self.change_login_handler()
                        self.success_("Login Info updated successfully!")
                    else:
                        self.error_("Invalid password")
                except Exception as ex:
                    self.error_("Error: %s" % ex.message)
                return redirect(url_for("Login:account_settings"))

            @route("/change-password", methods=["POST"])
            @login_required
            def change_password(self):
                try:
                    confirm_password = request.form.get("confirm-password").strip()
                    if current_user.password_matched(confirm_password):
                        self.change_password_handler()
                        self.success_("Password updated successfully!")
                    else:
                        self.error_("Invalid password")
                except Exception as ex:
                    self.error_("Error: %s" % ex.message)
                return redirect(url_for("Login:account_settings"))

            @route("/change-info", methods=["POST"])
            @login_required
            def change_info(self):
                name = request.form.get("name").strip()
                profile_pic_url = request.form.get("profile_pic_url").strip()

                data = {}
                if name and name != current_user.name:
                    data.update({"name": name})
                if profile_pic_url:
                    data.update({"profile_pic_url": profile_pic_url})
                if data:
                    current_user.update(**data)
                    self.success_("Account info updated successfully!")
                return redirect(url_for("Login:account_settings"))

            @route("/change-profile-pic", methods=["POST"])
            @login_required
            def change_profile_pic(self):
                profile_pic_url = request.form.get("profile_pic_url").strip()
                _ajax = request.form.get("_ajax", None)
                if profile_pic_url:
                    current_user.update(profile_pic_url=profile_pic_url)
                if _ajax:
                    return jsonify({})
                return redirect(url_for("Login:account_settings"))

        return view
    return wrapper


def login_view____(view, model,
               on_signout_view=None,
               on_signin_view="Index:index",
               template_dir=None):

    """
    :params model: The user model instance active-sqlachemy
    :view: The base view
    :on_signout_view: The view after logout
    :on_signin_view: The view after sign in
    :login_message: The message to show when login
    :allow_signup: To allow signup on the page
    :param template_dir: The directory containing the view pages

    Doc:
    Login is a view that allows you to login/logout use.
    You must create a Pylot view called `Login` to activate it

    LoginView = app.views.login(model=model.User, on_signin_view="Account:index")
    class Login(LoginView, Pylot):
        route_base = "/account"


    """


    view_name = view.__name__
    User = model.UserStruct.User

    # Login
    login_view = "%s:login" % view_name
    login_manager = LoginManager()
    login_manager.login_view = login_view
    login_manager.login_message_category = "error"

    Pylot.context_(COMPONENT_LOGIN=True)

    # Start binding
    Pylot.bind_(login_manager.init_app)

    @login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    if not template_dir:
        template_dir = "Pylot/Login"
    template_page = template_dir + "/%s.html"


    class Login(StorageUploadView):
        route_base = "/"

        SESSION_KEY_SET_EMAIL_DATA = "set_email_tmp_data"

        @classmethod
        def signup_handler(cls):
            """
            To handle the signup process. Must still bind to the app
             :returns User object:
            """
            if request.method == "POST":
                name = request.form.get("name")
                email = request.form.get("email")
                password = request.form.get("password")
                password2 = request.form.get("password2")
                profile_pic_url = request.form.get("profile_pic_url", None)

                if not name:
                    raise UserWarning("Name is required")
                elif not utils.is_valid_email(email):
                    raise UserWarning("Invalid email address '%s'" % email)
                elif not password.strip() or password.strip() != password2.strip():
                    raise UserWarning("Passwords don't match")
                elif not utils.is_valid_password(password):
                    raise UserWarning("Invalid password")
                else:
                    return User.new(email=email,
                                    password=password.strip(),
                                    name=name,
                                    profile_pic_url=profile_pic_url,
                                    signup_method="EMAIL")

        @classmethod
        def change_login_handler(cls, user_context=None, email=None):
            if not user_context:
                user_context = current_user
            if not email:
                email = request.form.get("email").strip()

            if not utils.is_valid_email(email):
                raise UserWarning("Invalid email address '%s'" % email)
            else:
                if email != user_context.email and User.get_by_email(email):
                    raise UserWarning("Email exists already '%s'" % email)
                elif email != user_context.email:
                    user_context.update(email=email)
                    return True
            return False

        @classmethod
        def change_password_handler(cls, user_context=None, password=None,
                                    password2=None):
            if not user_context:
                user_context = current_user
            if not password:
                password = request.form.get("password").strip()
            if not password2:
                password2 = request.form.get("password2").strip()

            if password:
                if password != password2:
                    raise UserWarning("Password don't match")
                elif not utils.is_valid_password(password):
                    raise UserWarning("Invalid password")
                else:
                    user_context.set_password(password)
                    return True
            else:
                raise UserWarning("Password is empty")

        @classmethod
        def reset_password_handler(cls, user_context=None,
                                   delivery=None,
                                   send_notification=True):
            """
            Reset the password
            :returns string: The new password string
            """
            if not user_context:
                user_context = current_user

            if delivery.upper() == "TOKEN":
                token = user_context.set_reset_password_token()
                if send_notification:
                    url = url_for("%s:reset_password_token" % view_name,
                                  token=token,
                                  _external=True)
                    mailer.send_template("reset-password-token.txt",
                                         to=user_context.email,
                                         name=user_context.name,
                                         reset_password_url=url
                                         )
                return token
            else:
                new_password = user_context.set_random_password()
                if send_notification:
                    url = url_for(login_manager.login_view, _external=True)
                    mailer.send_template("reset-password.txt",
                                         to=user_context.email,
                                         new_password=new_password,
                                         name=user_context.name,
                                         login_url=url
                                         )

        def _can_login(self):
            if not self.config_("LOGIN_EMAIL_ENABLE"):
                abort(403)

        def _can_oauth_login(self):
            if not self.config_("LOGIN_OAUTH_ENABLE"):
                abort(403)

        def _can_signup(self):
            if not self.config_("LOGIN_SIGNUP_ENABLE"):
                abort(403)

        def _login_user(self, user_context):
            login_user(user_context)
            user_context.update_last_login()
            user_context.update_last_visited()

        # --- LOGIN
        def login(self):
            """
            Login page
            """
            self._can_login()
            logout_user()
            self.meta_(title="Login")
            return self.render(login_url_next=request.args.get("next", ""),
                               view_template=template_page % "login")

        @route("email-login", methods=["POST"])
        def email_login(self):
            """
            login via email
            """
            self._can_login()

            email = request.form.get("email").strip()
            password = request.form.get("password").strip()

            if not email or not password:
                self.error_("Email or Password is empty")
                return redirect(url_for(login_view, next=request.form.get("next")))
            account = User.get_by_email(email)
            if account and account.password_matched(password):
                self._login_user(account)
                return redirect(request.form.get("next") or url_for(on_signin_view))
            else:
                self.error_("Email or Password is invalid")
                return redirect(url_for(login_view, next=request.form.get("next")))

        # OAUTH Login
        @route("oauth-login", methods=["POST"])
        def oauth_login(self):
            """
            To login via social
            """
            self._can_oauth_login()

            email = request.form.get("email").strip()
            name = request.form.get("name").strip()
            provider = request.form.get("provider").strip()
            provider_user_id = request.form.get("provider_user_id").strip()
            image_url = request.form.get("image_url").strip()
            next = request.form.get("next", "")
            # save to session and redirect to enter email address
            if not email:
                session[self.SESSION_KEY_SET_EMAIL_DATA] = {
                    "type": "social_login",
                    "email": email,
                    "name": name,
                    "provider": provider,
                    "provider_user_id": provider_user_id,
                    "image_url": image_url,
                    "next": next,
                    "signup_method": "SOCIAL:%s" % provider.upper()
                }
                return redirect(url_for("Login:set_email", next=request.form.get("next", "")))
            else:
                user = User.oauth_register(provider=provider,
                                           provider_user_id=provider_user_id,
                                           email=email,
                                           name=name,
                                           image_url=image_url,
                                           signup_method="SOCIAL:%s" % provider.upper())
                if user:
                    self._login_user(user)
                    return redirect(request.form.get("next") or url_for(on_signin_view))

            return redirect(url_for(login_view, next=request.form.get("next", "")))

        # OAUTH Login
        @route("oauth-connect", methods=["POST"])
        @login_required
        def oauth_connect(self):
            """
            To login via social
            """
            email = request.form.get("email").strip()
            name = request.form.get("name").strip()
            provider = request.form.get("provider").strip()
            provider_user_id = request.form.get("provider_user_id").strip()
            image_url = request.form.get("image_url").strip()
            next = request.form.get("next", "")
            try:
                current_user.oauth_connect(provider=provider,
                                         provider_user_id=provider_user_id,
                                         email=email,
                                         name=name,
                                         image_url=image_url)
            except Exception as ex:
                self.error_("Unable to link your account")

            return redirect(url_for("%s:account_settings" % view_name))

        # --- LOGOUT
        def logout(self):
            logout_user()
            self.success_("Logout successfully!")
            return redirect(url_for(on_signout_view or login_view))

        # --- LOST PASSWORD
        @route("lost-password", methods=["GET", "POST"])
        def lost_password(self):
            self._can_login()
            self.meta_(title="Lost Password")
            if request.method == "POST":
                email = request.form.get("email")
                user = User.get_by_email(email)
                if user:
                    delivery = self.config_("LOGIN_RESET_PASSWORD_DELIVERY")
                    self.reset_password_handler(user_context=user, delivery=delivery)
                    self.success_("A new password has been sent to '%s'" % email)
                else:
                    self.error_("Invalid email address")
                return redirect(url_for(login_view))
            else:
                logout_user()
                return self.render(view_template=template_page % "lost_password")

        @route("set-email", methods=["GET", "POST"])
        @login_required
        def set_email(self):
            self._can_login()
            self.meta_(title="Set Email")

            # Only user without email can set email
            if current_user.email:
                return redirect(url_for("%s:account_settings" % view_name))

            if request.method == "POST":
                email = request.form.get("email")
                if not utils.is_valid_email(email):
                    self.error_("Invalid email address '%s'" % email)
                    return redirect(url_for(login_view))

                if email and self.SESSION_KEY_SET_EMAIL_DATA in session:
                    _data = session[self.SESSION_KEY_SET_EMAIL_DATA]
                    user = User.get_by_email(email)
                    if user:
                        self.error_("An account is already using '%s'" % email)
                    else:
                        User.new(email=email,
                                 name=_data["name"],
                                 signup_method=_data["signup_method"] if "signup_method" in _data else "" )

                        if "type" in _data:
                            if _data["type"] == "social_login":
                                user = User.social_login(provider=_data["provider"],
                                                         provider_user_id=_data["provider_user_id"],
                                                         email=email,
                                                         name=_data["name"],
                                                         image_url=_data["image_url"])
                                return redirect(request.form.get("next") or url_for(on_signin_view))

                    return redirect(url_for("%s:set_email" % view_name,
                                            next=request.form.get("next", "")))
            else:
                return self.render(view_template=template_page % "set_email")

        # --- RESET PASSWORD
        @route("reset-password-token/<token>")
        def reset_password_token(self, token):
            self._can_login()
            user = User.get_by_token(token)
            if not user:
                self.error_("Invalid reset password token. Please try again")
                return redirect(url_for("%s:lost_password" % view_name))
            else:
                self._login_user(user)
                return redirect(url_for("%s:reset_password" % view_name))

        @route("reset-password", methods=["GET", "POST"])
        @login_required
        def reset_password(self):
            self._can_login()
            self.meta_(title="Reset Password")
            if current_user.require_password_change:
                if request.method == "POST":
                    try:
                        self.change_password_handler()
                        current_user.clear_reset_password_token()
                        self.success_("Password updated successfully!")
                        return redirect(url_for(on_signin_view))
                    except Exception as ex:
                        self.error_("Error: %s" % ex.message)
                        return redirect(url_for("%s:reset_password" % view_name))
                return self.render(view_template=template_page % "reset_password")
            return redirect(url_for(on_signin_view))

        # --
        @route("signup", methods=["GET", "POST"])
        def signup(self):
            self._can_login()
            self._can_signup()
            self.meta_(title="Signup")
            if request.method == "POST":
                # reCaptcha
                if not recaptcha.verify():
                    self.error_("Invalid Security code")
                    return redirect(url_for("Login:signup", next=request.form.get("next")))
                try:
                    new_account = self.signup_handler()
                    login_user(new_account)
                    self.success_("Congratulations! ")
                    return redirect(request.form.get("next") or url_for(on_signin_view))
                except Exception as ex:
                    self.error_(ex.message)
                return redirect(url_for("%s:signup" % view_name, next=request.form.get("next")))

            logout_user()
            return self.render(login_url_next=request.args.get("next", ""),
                               view_template=template_page % "signup")

        # --------

        @route("/account-settings")
        @login_required
        def account_settings(self):
            self.meta_(title="Account Settings")
            return self.render(view_template=template_page % "account_settings")

        @route("/change-login", methods=["POST"])
        @login_required
        def change_login(self):
            confirm_password = request.form.get("confirm-password").strip()
            try:
                if current_user.password_matched(confirm_password):
                    self.change_login_handler()
                    self.success_("Login Info updated successfully!")
                else:
                    self.error_("Invalid password")
            except Exception as ex:
                self.error_("Error: %s" % ex.message)
            return redirect(url_for("Login:account_settings"))

        @route("/change-password", methods=["POST"])
        @login_required
        def change_password(self):
            try:
                confirm_password = request.form.get("confirm-password").strip()
                if current_user.password_matched(confirm_password):
                    self.change_password_handler()
                    self.success_("Password updated successfully!")
                else:
                    self.error_("Invalid password")
            except Exception as ex:
                self.error_("Error: %s" % ex.message)
            return redirect(url_for("Login:account_settings"))

        @route("/change-info", methods=["POST"])
        @login_required
        def change_info(self):
            name = request.form.get("name").strip()
            profile_pic_url = request.form.get("profile_pic_url").strip()

            data = {}
            if name and name != current_user.name:
                data.update({"name": name})
            if profile_pic_url:
                data.update({"profile_pic_url": profile_pic_url})
            if data:
                current_user.update(**data)
                self.success_("Account info updated successfully!")
            return redirect(url_for("Login:account_settings"))

        @route("/change-profile-pic", methods=["POST"])
        @login_required
        def change_profile_pic(self):
            profile_pic_url = request.form.get("profile_pic_url").strip()
            _ajax = request.form.get("_ajax", None)
            if profile_pic_url:
                current_user.update(profile_pic_url=profile_pic_url)
            if _ajax:
                return jsonify({})
            return redirect(url_for("Login:account_settings"))
    return Login

# ------------------------------------------------------------------------------


def user_admin_view(model, login_view="Login", template_dir=None):
    """
    :param UserStruct: The User model structure containing other classes
    :param login_view: The login view interface
    :param template_dir: The directory containing the view pages
    :return: UserAdmin

    Doc:
    User Admin is a view that allows you to admin users.
    You must create a Pylot view called `UserAdmin` to activate it

    UserAdmin = app.views.user_admin(User, Login)
    class UserAdmin(UserAdmin, Pylot):
        pass

    The user admin create some global available vars under '__.user_admin'

    It's also best to add some security access on it
    class UserAdmin(UserAdmin, Pylot):
        decorators = [login_required]

    You can customize the user info page (::get) by creating the directory in your
    templates dir, and include the get.html inside of it

    ie:
    >/admin/templates/UserAdmin/get.html

    <div>
        {% include "Pylot/UserAdmin/get.html" %}
    <div>

    <div>Hello {{ __.user_admin.user.name }}<div>

    """

    Pylot.context_(COMPONENT_USER_ADMIN=True)

    User = model.UserStruct.User
    LoginView = login_view

    if not template_dir:
        template_dir = "Pylot/UserAdmin"
    template_page = template_dir + "/%s.html"

    class UserAdmin(object):
        route_base = "user-admin"

        @classmethod
        def _options(cls):
            return {
                "user_role": [("Rol", "Role")], #[(role, role) for i, role in enumerate(.all_roles)],
                "user_status": [("Sta", "Stat")] #[(status, status) for i, status in enumerate(User.all_status)]
            }

        @classmethod
        def search_handler(cls, per_page=20):
            """
            To initiate a search
            """
            page = request.args.get("page", 1)
            show_deleted = True if request.args.get("show-deleted") else False
            name = request.args.get("name")
            email = request.args.get("email")

            users = User.all(include_deleted=show_deleted)
            users = users.order_by(User.name.asc())
            if name:
                users = users.filter(User.name.contains(name))
            if email:
                users = users.filter(User.email.contains(email))

            users = users.paginate(page=page, per_page=per_page)

            cls.__(user_admin=dict(
                options=cls._options(),
                users=users,
                search_query={
                       "excluded_deleted": request.args.get("show-deleted"),
                       "role": request.args.get("role"),
                       "status": request.args.get("status"),
                       "name": request.args.get("name"),
                       "email": request.args.get("email")
                    }
                ))
            return users

        @classmethod
        def get_user_handler(cls, id):
            """
            Get a user
            """
            user = User.get(id, include_deleted=True)
            if not user:
                abort(404, "User doesn't exist")
            cls.__(user_admin=dict(user=user, options=cls._options()))
            return user

        def index(self):
            self.search_handler()
            return self.render(view_template=template_page % "index")

        def get(self, id):
            self.get_user_handler(id)
            return self.render(view_template=template_page % "get")

        def post(self):
            try:
                id = request.form.get("id")
                user = User.get(id, include_deleted=True)
                if not user:
                    self.error_("Can't change user info. Invalid user")
                    return redirect(url_for("UserAdmin:index"))

                delete_entry = True if request.form.get("delete-entry") else False
                if delete_entry:
                    user.update(status=user.STATUS_SUSPENDED)
                    user.delete()
                    self.success_("User DELETED Successfully!")
                    return redirect(url_for("UserAdmin:get", id=id))

                email = request.form.get("email")
                password = request.form.get("password")
                password2 = request.form.get("password2")
                name = request.form.get("name")
                role = request.form.get("user_role")
                status = request.form.get("user_status")
                upd = {}
                if email and email != user.email:
                    LoginView.change_login_handler(user_context=user)
                if password and password2:
                    LoginView.change_password_handler(user_context=user)
                if name != user.name:
                    upd.update({"name": name})
                if role and role != user.role:
                    upd.update({"role": role})
                if status and status != user.status:
                    if user.is_deleted and status == user.STATUS_ACTIVE:
                        user.delete(False)
                    upd.update({"status": status})
                if upd:
                    user.update(**upd)
                self.success_("User's Info updated successfully!")

            except Exception as ex:
                self.error_("Error: %s " % ex.message)
            return redirect(url_for("UserAdmin:get", id=id))


        @route("reset-password", methods=["POST"])
        def reset_password(self):
            try:
                id = request.form.get("id")
                user = User.get(id)
                if not user:
                    self.error_("Can't reset password. Invalid user")
                    return redirect(url_for("User:index"))

                password = LoginView.reset_password_handler(user_context=user)
                self.success_("User's password reset successfully!")
            except Exception as ex:
                self.error_("Error: %s " % ex.message)
            return redirect(url_for("UserAdmin:get", id=id))

        @route("create", methods=["POST"])
        def create(self):
            try:
                account = LoginView.signup_handler()
                account.set_role(request.form.get("role", "USER"))
                self.success_("User created successfully!")
                return redirect(url_for("UserAdmin:get", id=account.id))
            except Exception as ex:
                self.error_("Error: %s" % ex.message)
            return redirect(url_for("UserAdmin:index"))

    return UserAdmin


def post_manager_view(model, view="PostManager", template_dir=None):
    """
    :param PostStruct:
    """

    PostStruct = model.PostStruct

    Pylot.context_(COMPONENT_POST_MANAGER=True)

    if not template_dir:
        template_dir = "Pylot/PostManager"
    template_page = template_dir + "/%s.html"

    class PostManager(StorageUploadView):
        route_base = "post-manager"

        __session_edit_key = "post_manager_edit_post"

        def __init__(self):
            self.meta_(title=" | Post Manager", description="Post Manager to admin site")
            self.per_page = 25

        def index(self):
            """
            List all posts
            """
            self.meta_(title__prepend="All Posts")
            page = request.args.get("page", 1)
            id = request.args.get("id", None)
            slug = request.args.get("slug", None)
            status = request.args.get("status", "all")
            user_id = request.args.get("user_id", None)
            type_id = request.args.get("type_id", None)
            category_id = request.args.get("category_id", None)

            posts = PostStruct.Post.all()

            if id:
                posts = posts.filter(PostStruct.Post.id == id)
            if slug:
                posts = posts.filter(PostStruct.Post.slug == slug)
            if user_id:
                posts = posts.filter(PostStruct.Post.user_id == user_id)
            if type_id:
                posts = posts.filter(PostStruct.Post.type_id == type_id)
            if category_id:
                posts = posts.join(PostStruct.PostCategory)\
                    .join(PostStruct.Category)\
                    .filter(PostStruct.Category.id == category_id)
            if status == "publish":
                posts = posts.filter(PostStruct.Post.is_published == True)
            elif status == "draft":
                posts = posts.filter(PostStruct.Post.is_draft == True)
            elif status == "revision":
                posts = posts.filter(PostStruct.Post.is_revision == True)

            posts = posts.order_by(PostStruct.Post.id.desc())
            posts = posts.paginate(page=page, per_page=self.per_page)

            return self.render(posts=posts,
                               query_vars={
                                   "id": id,
                                   "slug": slug,
                                   "user_id": user_id,
                                   "type_id": type_id,
                                   "status": status
                               },
                               view_template=template_page % "index")

        def read(self, id):
            """
            Read Post
            """
            post = PostStruct.Post.get(id)
            if not post:
                abort(404, "Post doesn't exist")

            self.meta_(title__prepend=post.title)
            self.meta_(title__prepend="Read Post: ")

            return self.render(post=post,
                               view_template=template_page % "read")

        @route("upload-image", methods=["POST"])
        def upload_image(self):
            """
            Placeholder for markdown
            """

            url = ""
            if request.files.get("file"):
                url = storage.put(request.files.get('file'))

            else:
                return "Couldn't upload file. No file exist", 401

            return self.render(file_url=url)

            # For when there is an error
            error = False
            if error:
                return "error message", 401

            return jsonify({
                "id": "",
                "url": "", # full image url
            })

        @route("new", defaults={"id": None}, endpoint="PostManager:new")
        @route("edit/<id>", endpoint="PostManager:edit")
        def edit(self, id):
            """
            Create / Edit Post
            """
            self.meta_(title__prepend="Edit Post")

            types = [(t.id, t.name) for t in PostStruct.Type.all().order_by(PostStruct.Type.name.asc())]
            categories = [(c.id, c.name) for c in PostStruct.Category.all().order_by(PostStruct.Category.name.asc())]
            checked_cats = []
            post = {
                "id": 0,
                "title": "",
                "content": "",
                "slug": "",
                "type_id": 0
            }

            # saved in session
            if request.args.get("error") and self.__session_edit_key in session:
                post = session[self.__session_edit_key]
                checked_cats = post["post_categories"]
                del session[self.__session_edit_key]

            elif id:
                post = PostStruct.Post.get(id)
                if not post or post.is_revision:
                    abort(404, "Post doesn't exist")
                checked_cats = [c.id for c in post.categories]

            return self.render(post=post,
                               types=types,
                               categories=categories,
                               checked_categories=checked_cats,
                               view_template=template_page % "edit"
                              )

        def post(self):
            """
            Submit
            """
            id = request.form.get("id", None)
            title = request.form.get("title", None)
            slug = request.form.get("slug", None)
            content = request.form.get("content", None)
            type_id = request.form.get("type_id", None)
            post_categories = request.form.getlist("post_categories")
            published_date = request.form.get("published_date", None)
            status = request.form.get("status", "draft")
            is_published = True if status == "publish" else False
            is_draft = True if status == "draft" else False
            is_public = request.form.get("is_public", True)

            if status in ["draft", "publish"] and (not title or not type_id):
                if not title:
                    self.error_("Post Title is missing ")
                if not type_id:
                    self.error_("Post type is missing")

                session[self.__session_edit_key] = {
                    "id": id,
                    "title": title,
                    "content": content,
                    "slug": slug,
                    "type_id": type_id,
                    "published_date": published_date,
                    "post_categories": post_categories
                }
                if id:
                    url = url_for("PostManager:edit", id=id, error=1)
                else:
                    url = url_for("PostManager:new", error=1)
                return redirect(url)

            data = {
                "title": title,
                "content": content,
                "type_id": type_id
            }

            if published_date:
                published_date = datetime.datetime.strptime(published_date, "%Y-%m-%d %H:%M:%S")
            else:
                published_date = datetime.datetime.now()

            if id and status in ["delete", "revision"]:
                post = PostStruct.Post.get(id)
                if not post:
                    abort(404, "Post '%s' doesn't exist" % id)

                if status == "delete":
                    post.delete()
                    self.success_("Post deleted successfully!")
                    return redirect(url_for("%s:index" % view ))

                elif status == "revision":
                    data.update({
                        "user_id": current_user.id,
                        "parent_id": id,
                        "is_revision": True,
                        "is_draft": False,
                        "is_published": False,
                        "is_public": False
                    })
                    post = PostStruct.Post.create(**data)
                    return jsonify({"revision_id": post.id})

            elif status in ["draft", "publish"]:
                data.update({
                    "is_published": is_published,
                    "is_draft": is_draft,
                    "is_revision": False,
                    "is_public": is_public
                })
                if id:
                    post = PostStruct.Post.get(id)
                    if not post:
                        abort(404, "Post '%s' doesn't exist" % id)
                    elif post.is_revision:
                        abort(403, "Can't access this post")
                    else:
                        post.update(**data)
                else:
                    data["user_id"] = current_user.id
                    if is_published:
                        data["published_date"] = published_date
                    post = PostStruct.Post.create(**data)

                post.set_slug(slug or title)

                post.replace_categories(map(int, post_categories))

                if post.is_published and not post.published_date:
                    post.update(published_date=published_date)

                self.success_("Post saved successfully!")

                endpoint = "read" if post.is_published else "edit"
                return redirect(url_for("%s:%s" % (view, endpoint), id=post.id))

            else:
                abort(400, "Invalid post status")

        @route("categories", methods=["GET", "POST"])
        def categories(self):
            self.meta_(title__prepend="Post Categories")
            if request.method == "POST":
                id = request.form.get("id", None)
                action = request.form.get("action")
                name = request.form.get("name")
                slug = request.form.get("slug", None)
                ajax = request.form.get("ajax", False)
                try:
                    if not id:
                        cat = PostStruct.Category.new(name=name, slug=slug)
                        if ajax:
                            return jsonify({
                                "id": cat.id,
                                "name": cat.name,
                                "slug": cat.slug,
                                "status": "OK"
                            })
                        self.success_("New category '%s' added" % name)
                    else:
                        post_cat = PostStruct.Category.get(id)
                        if post_cat:
                            if action == "delete":
                                post_cat.delete()
                                self.success_("Category '%s' deleted successfully!" % post_cat.name)
                            else:
                                post_cat.update(name=name, slug=slug)
                                self.success_("Category '%s' updated successfully!" % post_cat.name)
                except Exception as ex:
                    if ajax:
                        return jsonify({
                            "error": True,
                            "error_message": ex.message
                        })

                    self.error_("Error: %s" % ex.message)
                return redirect(url_for("%s:categories" % view))

            else:
                cats = PostStruct.Category.all().order_by(PostStruct.Category.name.asc())
                return self.render(categories=cats,
                                   view_template=template_page % "categories")

        @route("types", methods=["GET", "POST"])
        def types(self):
            self.meta_(title__prepend="Post Types")
            if request.method == "POST":
                try:
                    id = request.form.get("id", None)
                    action = request.form.get("action")
                    name = request.form.get("name")
                    slug = request.form.get("slug", None)
                    if not id:
                        PostStruct.Type.new(name=name, slug=slug)
                        self.success_("New type '%s' added" % name)
                    else:
                        post_type = PostStruct.Type.get(id)
                        if post_type:
                            if action == "delete":
                                post_type.delete()
                                self.success_("Type '%s' deleted successfully!" % post_type.name)
                            else:
                                post_type.update(name=name, slug=slug)
                                self.success_("Type '%s' updated successfully!" % post_type.name)
                except Exception as ex:
                    self.error_("Error: %s" % ex.message)
                return redirect(url_for("%s:types" % view))
            else:
                types = PostStruct.Type.all().order_by(PostStruct.Type.name.asc())
                return self.render(types=types,
                                   view_template=template_page % "types")

    return PostManager


def post_front_view(category):

    class Post(object):

        def index(self):
            pass

        def get(self):
            pass


def contact_view(view):
    @view.extends_
    @route("contact", methods=["GET", "POST"])
    def contact(self):
        """
        Contact view
        """

        view_name = view.__name__
        template_dir = "Pylot/Contact"
        template_page = "%s/contact.html" % template_dir

        if request.method == "POST":
            error_message = None
            email = request.form.get("email")
            subject = request.form.get("subject")
            message = request.form.get("message")
            name = request.form.get("name")

            contact_email = self.config_("CONTACT_PAGE_EMAIL_RECIPIENT")
            if recaptcha.verify():
                if not email or not subject or not message:
                    error_message = "All fields are required"
                elif not utils.is_valid_email(email):
                    error_message = "Invalid email address"
                if error_message:
                    self.error_(error_message)
                else:
                    mailer.send_template("contact-us.txt",
                                         to=contact_email,
                                         reply_to=email,
                                         mail_from=email,
                                         mail_subject=subject,
                                         mail_message=message,
                                         mail_name=name
                                        )
                    self.success_("Message sent successfully! We'll get in touch with you soon.")
            else:
                self.error_("Invalid security code")
            return redirect(url_for("%s:contact" % view_name))
        else:
            submit_url = url_for('%s:contact' % view_name)
            self.meta_(title="Contact Us")
            return self.render(__post_url__=submit_url,
                               view_template=template_page)
    return view



# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------



def maintenance_view(template=None):
    """
    Create the Maintenance view
    Must be instantiated

    import maintenance_view
    MaintenanceView = maintenance_view()

    :param view_template: The directory containing the view pages
    :return:
    """
    if not template:
        template = "Pylot/Maintenance/index.html"

    class Maintenance(Pylot):
        @classmethod
        def register(cls, app, **kwargs):
            super(cls, cls).register(app, **kwargs)

            if cls.config_("MAINTENANCE_ON"):
                @app.before_request
                def on_maintenance():
                    return cls.render(layout=template), 503
    return Maintenance

MaintenanceView = maintenance_view()

def error_view(template_dir=None):
    """
    Create the Error view
    Must be instantiated

    import error_view
    ErrorView = error_view()

    :param template_dir: The directory containing the view pages
    :return:
    """
    if not template_dir:
        template_dir = "Pylot/Error"

    template_page = "%s/index.html" % template_dir

    class Error(Pylot):
        """
        Error Views
        """
        @classmethod
        def register(cls, app, **kwargs):
            super(cls, cls).register(app, **kwargs)

            @app.errorhandler(400)
            def error_400(error):
                return cls.index(error, 400)

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
            cls.meta_(title="Error %s" % code)

            return cls.render(error=error, view_template=template_page), code
    return Error
ErrorView = error_view()


# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------


# Extend JINJA Filters

def to_date(dt, format="%m/%d/%Y"):
    return "" if not dt else dt.strftime(format)

def strip_decimal(amount):
    return amount.split(".")[0]

def bool_to_yes(b):
    return "Yes" if b is True else "No"

def bool_to_int(b):
    return 1 if b is True else 0

def nl2br(s):
    """
    {{ s|nl2br }}

    Convert newlines into <p> and <br />s.
    """
    if not isinstance(s, basestring):
        s = str(s)
    s = re.sub(r'\r\n|\r|\n', '\n', s)
    paragraphs = re.split('\n{2,}', s)
    paragraphs = ['<p>%s</p>' % p.strip().replace('\n', '<br />') for p in paragraphs]
    return '\n\n'.join(paragraphs)


jinja2.filters.FILTERS.update({
    "currency": utils.to_currency,
    "strip_decimal": strip_decimal,
    "date": to_date,
    "int": int,
    "slug": utils.slug,
    "intcomma": humanize.intcomma,
    "intword": humanize.intword,
    "naturalday": humanize.naturalday,
    "naturaldate": humanize.naturaldate,
    "naturaltime": humanize.naturaltime,
    "naturalsize": humanize.naturalsize,
    "bool_to_yes": bool_to_yes,
    "bool_to_int": bool_to_int,
    "nl2br": nl2br,
    "markdown": mistune.markdown
})
