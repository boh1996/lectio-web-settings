from flask import Flask
from flask import redirect
from flask import request
import config
from GoogleOAuth import google_oauth as GoogleOAuth
from GoogleCalendar import calendar as GoogleCalendar
from flask.ext.sqlalchemy import SQLAlchemy
from app import *
from objects import *
import string
import random
import json
from flask import Response
from GoogleOAuth.error import Error

db.create_all()

# Creates a random string
def createToken (size=32, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))

# Initialize Google OAuth module
GoogleOAuth = GoogleOAuth.GoogleOAuth()

# Create All DB force route
@application.route('/start', methods=['GET'])
def index():
    db.create_all()
    return "Service Running"

# Starting auth route
@application.route('/auth', methods=['GET'])
def auth():
    return json.dumps({
        "status" : "ok",
        "url" : GoogleOAuth.auth(callback="/callback",state="auth")
    })

@application.after_request
def after_request(response):
    response.headers.add("Content-Type", "application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Return from Google Auth callback
@application.route("/callback")
def callback():

    # If error
    if request.args.get("error") != False :
        data = GoogleOAuth.callback(code=request.args.get("code"))

        # If no callback data has been returned or the request failed
        if not isinstance(data, Error) and hasattr(data, "access_token"):
            userdata = GoogleOAuth.userinfo(data.access_token)

            # If no user data has been returned, then the access token isn't valid
            if userdata != False:
                if data.refresh_token != "NULL":
                    db.session.add(User(userdata.id, data.refresh_token))
                    db.session.commit()
                    token = createToken(32)
                    db.session.add(UserToken(token, data.access_token, data.expires_in, userdata.id))
                    db.session.commit()

                    # Create session
                    return json.dumps({
                        "token" : token,
                        "status" : "ok",
                        "user" : userdata.__dict__,
                        "created" : True
                    })
                else:
                    token = createToken(32)
                    db.session.add(UserToken(token, data.access_token, data.expires_in, userdata.id))
                    db.session.commit()

                    # Create session
                    return json.dumps({
                        "token" : token,
                        "created" : False,
                        "status" : "ok",
                        "user" : userdata.__dict__
                    })
            else:
                return json.dumps({
                    "status" : "error",
                    "error" : "No user data fetched",
                    "error_code" : "404"
                })
        else:
            return json.dumps({
                "status" : "error",
                "error" : "No access token fetched",
                "error_code" : "403",
                "error_message" : data.error
            })
    else:
        return json.dumps({
            "status" : "error",
            "error" : request.args.get("error"),
            "error_code" : 500,
        })

# Run the app/server
if __name__ == '__main__':
    application.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )