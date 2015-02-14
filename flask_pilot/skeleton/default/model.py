"""
Flask-Pilot models

model.py

You may place your models here.
"""

from active_sqlalchemy import SQLAlchemy
from . import get_config_env
import config

conf = get_config_env(config)

db = SQLAlchemy(conf.SQLALCHEMY_DATABASE_URI)


class Test(db.Model):
    name = db.Column(db.String(120))
    last_updated = db.Column(db.DateTime)