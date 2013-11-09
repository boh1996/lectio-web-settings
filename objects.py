from flask import Flask
from flask import redirect
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from app import db
from datetime import *
from time import mktime

# The User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    refresh_token = db.Column(db.String(255))

    def __init__(self, user_id, refresh_token):
        self.user_id = user_id
        self.refresh_token = refresh_token

    def __repr__(self):
        return '<User %r>' % self.id

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