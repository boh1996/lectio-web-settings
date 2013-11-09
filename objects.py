from flask import Flask
from flask import redirect
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from app import db
from datetime import *
import json
from time import mktime

def to_json(inst, cls, exclude=[]):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.name not in exclude:
            if c.type in convert.keys() and v is not None:
                try:
                    d[c.name] = convert[c.type](v)
                except:
                    d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
            elif v is None:
                d[c.name] = str()
            else:
                d[c.name] = v
    return json.dumps(d)

# The User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    refresh_token = db.Column(db.String(255))
    school_id = db.Column(db.String(45))
    branch_id = db.Column(db.String(45))
    lectio_user_id = db.Column(db.String(45))
    username = db.Column(db.String(45))
    password = db.Column(db.String(45))

    def __init__(self,
        user_id,
            refresh_token,
            school_id = "",
            branch_id = "",
            lectio_user_id = "",
            username = "",
            password = "",
        ):
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.school_id = school_id
        self.branch_id = branch_id
        self.lectio_user_id = lectio_user_id
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.id

    @property
    def json(self):
        return to_json(self, self.__class__,["password","username"])

class UserToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    created_at = db.Column(db.String(45), default=str(mktime(datetime.now().timetuple()))[:-2])
    expires_at = db.Column(db.String(45))
    user_id = db.Column(db.String(255),db.ForeignKey("user.user_id"), nullable=False)

    def __init__(self, token, access_token, expires_in, user_id):
        self.access_token = access_token
        self.token = token
        self.user_id = user_id
        self.expires_at = str(mktime(datetime.now().timetuple()) + expires_in)[:-2]

    def __repr__(self):
        return '<UserToken %r>' % self.id

    @property
    def json(self):
        return to_json(self, self.__class__)

# School Object, taken from Lectio API
class School(db.Model):
    __tablename__ = "schools"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    school_id = db.Column(db.Integer(45))
    school_branch_id = db.Column(db.Integer(45))

    def __init__(self, name, school_id, school_branch_id):
        self.name = name
        self.school_id = school_id
        self.school_branch_id = school_branch_id

    def __repr__(self):
        return '<School %r>' % self.id

    @property
    def json(self):
        return to_json(self, self.__class__)

# Access token model
class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=False)
    access_token = db.Column(db.String(80), unique=True)
    expires_in = db.Column(db.String(45))

    def __init__(self, user_id, access_token, expires_in):
        self.access_token = access_token
        self.user_id = user_id
        self.expires_in = expires_in

    def __repr__(self):
        return '<AccessToken %r>' % self.id

    @property
    def json(self):
        return to_json(self, self.__class__)