"""
Pylot
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

from pylot.component.views import (login_view,
                                   contact_view,
                                   user_admin_view,
                                   post_manager_view)

from application import model

UserAdminView = user_admin_view(model)
PostManagerView = post_manager_view(model)

@login_view(model=model)
class Login(Pylot):
    route_base = "/"


"""
@user_admin_view(model=model)
class UserAdmin(Pylot):
    pass

@post_manager_view
class PostManager(PostManagerView, Pylot):
    pass
"""


@contact_view
class Index(Pylot):
    route_base = "/"

    def index(self):
        self.meta_(title="Hello Pylot!")
        return self.render()

    @route("upload", methods=["GET", "POST"])
    def upload(self):
        url = ""
        if request.method == "POST":
            url = self.storage.put(request.files.get('file'))
        return self.render(file_url=url)

# Example
class Example(Pylot):
    def index(self):
        self.meta_(title="Example Page")
        self.error_("This is an error message set by error_ and called with show_flashed_message()")
        self.success_("This is a success message set by error_ and called with show_flashed_message()")
        return self.render()

