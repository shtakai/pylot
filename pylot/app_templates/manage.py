"""
Pylot command line tool

manage.py

Command line tool to manage your application

"""

import argparse
from application import get_config
import application.model as model
from pylot import utils

config = get_config()
NAME = "Pylot Manager"
__version__ = config.APP_VERSION

def setup():

    # Create all db
    model.db.create_all()

    roles = ["user", "admin", "superadmin"]

    # Setup the SUPERADMIN
    email = config.ADMIN_EMAIL
    name = config.ADMIN_NAME
    user = model.User.get_by_email(email)
    if not user:
        model.User.User.new(email=email,
                            name=name,
                            role="SUPERADMIN")


def main():
    parser = argparse.ArgumentParser(description="%s  v.%s" % (NAME, __version__))
    parser.add_argument("--setup", help="Setup the system",  action="store_true")
    parser.add_argument("--upload-static-to-s3", help="Upload all static files to S3", action="store_true")
    arg = parser.parse_args()

    if arg.setup:
        # Default setup
        print("Setting up...")
        setup()

    if arg.upload_static_to_s3:
        # Upload static files to s3
        import flask_s3
        import run_www  # Or the main application run file
        print("Upload static files to S3")
        flask_s3.create_all(run_www.app)

if __name__ == "__main__":
    main()


