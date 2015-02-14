"""
Flask-Pilot

Flask-Pilot is a Flask extension that adds structure to both your views and
templates, by mapping them to each other to provide a rapid application development framework.
The extension also comes with Flask-Classy, Flask-Assets, Flask-Mail,
JQuery 2.x, Bootstrap 3.x, Font-Awesome, Bootswatch templates.
The extension also provides pre-made templates for error pages and macros.

https://github.com/mardix/flask-pilot

"""

from setuptools import setup, find_packages

__NAME__ = "Flask-Pilot"
__version__ = "0.1.0"
__author__ = "Mardix"
__license__ = "MIT"
__copyright__ = "(c) 2014 Mardix"


setup(
    name=__NAME__,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email='mardix@github.com',
    description="Flask-Pilot is a Flask extension that adds structure and map your views and templates together for rapid application development",
    long_description=__doc__,
    url='http://mardix.github.io/flask-pilot/',
    download_url='http://github.com/mardix/flask-pilot/tarball/master',
    py_modules=['flask_pilot'],
    entry_points=dict(console_scripts=['flask-pilot=flask_pilot.cmd:main']),
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Flask==0.10.1',
        'Flask-Classy==0.6.10',
        'Flask-Assets==0.10',
        'Flask-Mail==0.9.1',
        'Flask-WTF==0.11',
        'Active-SQLAlchemy==0.3.2'
    ],

    keywords=['flask', 'templates', 'views', 'classy', 'pilot', 'framework', "mvc", "blueprint"],
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
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)
