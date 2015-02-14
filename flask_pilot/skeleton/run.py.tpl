"""
Flask-Pilot : run.py
To launch the server
"""

import os
from flask import Flask
from flask_pilot import Pilot

# Import get_env for the system environment
from {project_name} import get_env

# Import the application's views
import {project_name}.views

# Project conf environment. Dev=Development, Prod=Production
project_env = get_env()

# The project configuration relative to $project_name.module.class
project_config = "config.%s" % (project_env)

# Pilot.init returns the flask_app instance
app = Pilot.init(Flask(__name__), config=project_config)

if __name__ == "__main__":
    app.run()
