"""
Flask-Pilot : server_{project_name}.py
To launch the server
"""

from flask import Flask
from flask_pilot import Pilot

# Import get_env for the system environment to retrieve the environment
from {project_name} import get_env

# Import the application's views
import {project_name}.views

# The directory containing your views/static/templates
app_dir = "{project_name}"

# Get the environment: Dev=Development, Prod=Production. To help with config
app_env = get_env()

# The project config object
app_config = "{project_name}.config.%s" % app_env

# Pilot.init returns the flask_app instance
app = Pilot.init(Flask(__name__), directory=app_dir, config=app_config)

if __name__ == "__main__":
    app.run()
