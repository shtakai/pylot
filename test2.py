
from flask import Flask
from active_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

db = SQLAlchemy()

class User(db.Model):
    name = db.Column(db.String(25))
    location = db.Column(db.String(50), default="USA")
    last_access = db.Column(db.DateTime)

db.create_all()



@app.route("/")
def index():
    u = User.create(name="Jones")
    return "Hello %s" % u.name



if __name__ == "__main__":

    app.run(debug=True)