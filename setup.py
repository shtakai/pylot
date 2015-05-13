"""
Pylot

Pylot is a framework based on Flask extension that adds structure to both your views and
templates, by mapping them to each other to provide a rapid application development framework.
The extension also comes with Flask-Classy, Flask-Assets, Flask-Mail,
JQuery 2.x, Bootstrap 3.x, Font-Awesome, Bootswatch templates.
The extension also provides pre-made templates for error pages and macros.

https://github.com/mardix/flask-pilot

"""

from setuptools import setup, find_packages


def read_pkginfo(filename):
    """
    Help us read the pkginfo without accessing __init__
    """
    COMMENT_CHAR = '#'
    OPTION_CHAR =  '='
    options = {}
    f = open(filename)
    for line in f:
        if COMMENT_CHAR in line:
            line, comment = line.split(COMMENT_CHAR, 1)
        if OPTION_CHAR in line:
            option, value = line.split(OPTION_CHAR, 1)
            option = option.strip()
            value = value.strip()
            options[option] = value
    f.close()
    return options

pkginfo = read_pkginfo('./pylot/pkginfo.py')

__NAME__ = pkginfo["NAME"]
__version__ = pkginfo["VERSION"]
__author__ = pkginfo["AUTHOR"]
__license__ = pkginfo["LICENSE"]
__copyright__ = pkginfo["COPYRIGHT"]

setup(
    name=__NAME__,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email='mardix@github.com',
    description="Pylot is a Flask extension that adds structure and map your views and templates together for rapid application development",
    long_description=__doc__,
    url='https://github.com/mardix/pylot/',
    download_url='http://github.com/mardix/pylot/tarball/master',
    py_modules=['pylot'],
    entry_points=dict(console_scripts=[
        'pylot=pylot.cmd:main'
    ]),
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Flask==0.10.1',
        'Flask-Classy==0.6.10',
        'Flask-Assets==0.10',
        'flask-recaptcha==0.3',
        'flask-login==0.2.11',
        'flask-kvsession==0.6.1',
        'flask-s3==0.1.7',
        'flask-mail==0.9.1',
        'flask-cache==0.13.1',
        'flask-store==0.0.4.1',

        'Active-SQLAlchemy==0.3.4',
        'passlib==1.6.2',
        'bcrypt==1.1.1',
        'python-slugify==0.1.0',
        'humanize==0.5.1',
        'redis==2.9.1',
        'ses-mailer==0.12.0',
        'mistune==0.5.1',
        'wrapt==1.10.4',
    ],

    keywords=['flask',
              'pylot',
              'templates',
              'views',
              'classy',
              'pilot',
              'framework',
              "mvc",
              "blueprint"],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)
