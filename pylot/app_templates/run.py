"""
::Pylot::

run_{project_name}.py

To run the server
"""

from pylot import Pylot

# Import get_env for the system environment to retrieve the environment
from application import get_env

# Import the application's views
import application.{project_name}.views

# The directory containing your views/static/templates
app_dir = "application/{project_name}"

# Get the environment: Development, Production. To help with config
app_env = get_env()

# The project config object
app_config = "application.config.%s" % app_env

# Pylot.init returns Flask instance
app = Pylot.init(__name__, directory=app_dir, config=app_config)

if __name__ == "__main__":
    app.run()
