"""
Your views
"""

from pylot import (Pylot,
                   mailer,
                   storage,
                   route,
                   abort,
                   request,
                   redirect,
                   url_for,
                   jsonify,
                   session,
                   AppError)
from pylot.views import (login_view,
                         contact_view)

from application import model

LoginView = login_view(model.User)
ContactView = contact_view()

# Login
class Login(LoginView, Pylot):
    pass

# Index
class Index(ContactView, Pylot):
    route_base = "/"

    def index(self):
        self.meta_(title="Hello Pylot!")
        return self.render()

# Example
class Example(Pylot):
    def index(self):
        self.meta_(title="Example Page")
        self.flash_error_("This is an error message set by flash_error_ and called with show_flashed_message()")
        self.flash_success_("This is a success message set by flash_error_ and called with show_flashed_message()")
        return self.render()

