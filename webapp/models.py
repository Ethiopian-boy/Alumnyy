from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime

class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    fullname = db.Column(db.String(255))
    country = db.Column(db.String(255))
    school = db.Column(db.String(255))
    programme = db.Column(db.String(255))
    mobilenumber = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    avatar = db.Column(db.String(560))
    occupation = db.Column(db.String(255))
    organisation = db.Column(db.String(255))
    year = db.Column(db.Integer)
    bio = db.Column(db.String(800))
    password = db.Column(db.String(255))
    online = db.Column(db.Integer, default=0)
    post = db.relationship('post', backref='post')

    def __init__(self, fullname, country, school, programme, mobilenumber, 
                        email, occupation, organisation, year, password):
        self.date = datetime.datetime.now()
        self.fullname = fullname
        self.country = country
        self.school = school
        self.programme = programme
        self.mobilenumber = mobilenumber
        self.email = email
        self.avatar = None
        self.occupation = occupation
        self.organisation = organisation
        self.year = year
        self.bio = None
        self.online = 1
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.email

class school(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    logo = db.Column(db.String(255))

class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(10000))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))

class connect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initid = db.Column(db.Integer, db.ForeignKey('user.id'))
    recid = db.Column(db.Integer, db.ForeignKey('user.id'))

class approvedconnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    connecta = db.Column(db.Integer, db.ForeignKey('user.id'))
    connectb = db.Column(db.Integer, db.ForeignKey('user.id'))