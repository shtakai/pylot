"""
Pylot

Command line tool

pylot -c project_name

"""

import os
import argparse
import pkg_resources
import pylot

PACKAGE = pylot
CWD = os.getcwd()
SKELETON_DIR = "app_templates"
APPLICATION_DIR = "%s/application" % CWD

def get_project_dir_path(project_name):
    return "%s/%s" % (APPLICATION_DIR, project_name)

def copy_resource(src, dest):
    """
    To copy package data to destination
    """
    dest = (dest + "/" + os.path.basename(src)).rstrip("/")
    if pkg_resources.resource_isdir(PACKAGE.__name__, src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for res in pkg_resources.resource_listdir(__name__, src):
            copy_resource(src + "/" + res, dest)
    else:
        if os.path.splitext(src)[1] not in [".pyc"]:
            with open(dest, "wb") as f:
                f.write(pkg_resources.resource_string(__name__, src))


def create_project(project_name, template="default"):
    """
    Create the project
    """

    project_dir = get_project_dir_path(project_name)

    run_tpl = pkg_resources.resource_string(__name__, '%s/run.py' % (SKELETON_DIR))
    init_py_tpl = pkg_resources.resource_string(__name__, '%s/init.py' % (SKELETON_DIR))
    deployapp_tpl = pkg_resources.resource_string(__name__, '%s/deployapp.yml' % (SKELETON_DIR))
    config_tpl = pkg_resources.resource_string(__name__, '%s/config.py' % (SKELETON_DIR))
    model_tpl = pkg_resources.resource_string(__name__, '%s/model.py' % (SKELETON_DIR))
    manage_tpl = pkg_resources.resource_string(__name__, '%s/manage.py' % (SKELETON_DIR))

    run_file = "%s/run_%s.py" % (CWD, project_name)
    requirements_txt = "%s/requirements.txt" % CWD
    deployapp_yml = "%s/deployapp.yml" % CWD
    config_py = "%s/config.py" % APPLICATION_DIR
    model_py = "%s/model.py" % APPLICATION_DIR
    manage_py = "%s/manage.py" % CWD

    if not os.path.isdir(APPLICATION_DIR):
        os.makedirs(APPLICATION_DIR)

    if not os.path.isdir(project_dir):
        os.makedirs(project_dir)

    _app_init_py = "%s/__init__.py" % APPLICATION_DIR
    if not os.path.isfile(_app_init_py):
        with open(_app_init_py, "wb") as f:
            f.write(init_py_tpl)

    _init_py = "%s/__init__.py" % CWD
    if not os.path.isfile(_init_py):
        with open(_init_py, "wb") as f:
            f.write("# Pylot")

    if not os.path.isfile(config_py):
        with open(config_py, "wb") as f:
            f.write(config_tpl)

    if not os.path.isfile(model_py):
        with open(model_py, "wb") as f:
            f.write(model_tpl)

    if not os.path.isfile(run_file):
        with open(run_file, "wb") as f:
            f.write(run_tpl.format(project_name=project_name))

    if not os.path.isfile(requirements_txt):
        with open(requirements_txt, "wb") as f:
            f.write("%s==%s" % (PACKAGE.NAME, PACKAGE.__version__))

    if not os.path.isfile(deployapp_yml):
        with open(deployapp_yml, "wb") as f:
            f.write(deployapp_tpl)

    if not os.path.isfile(manage_py):
        with open(manage_py, "wb") as f:
            f.write(manage_tpl)

    copy_resource("%s/%s/" % (SKELETON_DIR, template), project_dir)


def main():
    _description = "%s %s" % (PACKAGE.NAME, PACKAGE.__version__)
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-c", "--create", help="To create a new project."
                             " [ie: pylot -c www]")

    arg = parser.parse_args()
    print(_description)
    if arg.create:
        project_name = arg.create
        template = "default"
        create_project(project_name, template)
        print("Created project: %s'" % project_name)
        print("To launch server run 'run_%s.py'" % project_name)




