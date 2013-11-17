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
from datetime import *
from time import mktime
import random
import json
from flask import Response
from GoogleOAuth.error import Error
from LectioAPI import authenticate

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

@application.route("/fetch/calendars")
def fetch_calendars():
    if request.args.get("token"):
        UserObject = db.session.query(User).join(UserToken,UserToken.user_id == User.user_id).filter(UserToken.token == request.args.get("token")).first()
        UsersToken = db.session.query(UserToken).filter(UserToken.token == request.args.get("token")).first()
        if isinstance(UserObject, User):

            # Refresh Google Token
            if int(UsersToken.expires_at) <= int(str(mktime(datetime.now().timetuple()))[:-2]):
                Token = GoogleOAuth.refresh(UserObject.refresh_token)
                UsersToken.access_token = Token.access_token
                UsersToken.expires_at = str(mktime(datetime.now().timetuple())+int(Token.expires_in))[:-2]
                db.session.add(UsersToken)
                db.session.commit()

            GoogleCalendarObject = GoogleCalendar.GoogleCalendar()
            GoogleCalendarObject.access_token = UsersToken.access_token
            colors = GoogleCalendarObject.colors()
            calendars = GoogleCalendarObject.calendars()

            return json.dumps({
                "status" : "ok",
                "calendars" : calendars,
                "colors" : colors
            })
        else:
            return json.dumps({
            "status" : "error",
            "error_code" : "403",
            "error_message" : "No token found!"
        }), 403
    else:
        return json.dumps({
            "status" : "error",
            "error_code" : "400",
            "error_message" : "No token supplied"
        }), 400

@application.route("/save/user-id", methods=["POST"])
def save_user_id():
    if request.args.get("token"):
        UserObject = db.session.query(User).join(UserToken,UserToken.user_id == User.user_id).filter(UserToken.token == request.args.get("token")).first()
        if isinstance(UserObject, User):
            incomming = json.loads(request.form.keys()[0])

            UserObject.lectio_user_id = incomming.student_id

            db.session.add(UserObject)
            db.session.commit()

            return json.dumps({
                "status" : "ok"
            })
        else:
            return json.dumps({
            "status" : "error",
            "error_code" : "403",
            "error_message" : "No token found!"
        }), 403
    else:
        return json.dumps({
            "status" : "error",
            "error_code" : "400",
            "error_message" : "No token supplied"
        }), 400


@application.route("/save/user", methods=["POST"])
def save_user():
    pass
    '''if request.args.get("token"):
        UserObject = db.session.query(User).join(UserToken,UserToken.user_id == User.user_id).filter(UserToken.token == request.args.get("token")).first()
        if isinstance(UserObject, User):
            incomming = json.loads(request.form.keys()[0])
            if hasattr(incomming,"username") and hasattr(incomming,"password"):
                UserObject.username = incomming.username
                UserObject.password = incomming.password

                return json.dumps({
                    "status" : "ok"
                })
            else:
        else:
            return json.dumps({
            "status" : "error",
            "error_code" : "403",
            "error_message" : "No token found!"
        }), 403
    else:
        return json.dumps({
            "status" : "error",
            "error_code" : "400",
            "error_message" : "No token supplied"
        }), 400'''

@application.route("/save/calendar",methods=["POST","GET"])
def save_calendar():
    if request.args.get("token"):
        UserObject = db.session.query(User).join(UserToken,UserToken.user_id == User.user_id).filter(UserToken.token == request.args.get("token")).first()
        if isinstance(UserObject, User):
            incomming = json.loads(request.form.keys()[0])
            ExistingTask = db.session.query(TimeTableTask).filter(google_id = UserObject.user_id).first()

            TaskObject = TimeTableTask(UserObject.user_id, "" ,incomming.simplify)

            if isinstance(ExistingTask, TimeTableTask):
                TaskObject = ExistingTask

            if incomming.calendar.type == "existing":
                TaskObject.calendar_id = incomming.calendar.id
            else:
                UsersToken = db.session.query(UserToken).filter(UserToken.token == request.args.get("token")).first()

                # Refresh Google Token
                if int(UsersToken.expires_at) <= int(str(mktime(datetime.now().timetuple()))[:-2]):
                    Token = GoogleOAuth.refresh(UserObject.refresh_token)
                    UsersToken.access_token = Token.access_token
                    UsersToken.expires_at = str(mktime(datetime.now().timetuple())+int(Token.expires_in))[:-2]
                    db.session.add(UsersToken)
                    db.session.commit()

                GoogleCalendarObject = GoogleCalendar.GoogleCalendar
                GoogleCalendarObject.access_token = UsersToken.access_token
                GoogleCalendarObject.createCalendar(incomming.calendar.name)

            db.session.add(TaskObject)
            db.session.commit()

            return json.dumps({
                "status" : "ok"
            })
        else:
            return json.dumps({
            "status" : "error",
            "error_code" : "403",
            "error_message" : "No token found!"
        }), 403
    else:
        return json.dumps({
            "status" : "error",
            "error_code" : "400",
            "error_message" : "No token supplied"
        }), 400



@application.route("/save/school", methods=["POST","GET"])
def save_school():
    if request.args.get("token"):
        UserObject = db.session.query(User).join(UserToken,UserToken.user_id == User.user_id).filter(UserToken.token == request.args.get("token")).first()
        if isinstance(UserObject, User):
            if "branch_id" in request.form:
                UserObject.branch_id = request.form["branch_id"]
            if "school_id" in request.form:
                UserObject.school_id = request.form["school_id"]
            db.session.add(UserObject)
            db.session.commit()

            return json.dumps({
                "status" : "ok"
            })
        else:
            return json.dumps({
            "status" : "error",
            "error_code" : "403",
            "error_message" : "No token found!"
        }), 403
    else:
        return json.dumps({
            "status" : "error",
            "error_code" : "400",
            "error_message" : "No token supplied"
        }), 400

@application.route("/students")
def students():
    if request.args.get("suggest") == False or request.args.get("suggest") == None:
        students = db.session.query(Student).filter(Student.school_branch_id==request.args.get("branch_id")).all()
    else:
        searchstring = request.args.get("suggest") + '%'
        students = db.session.query(Student).filter(Student.name.like(searchstring)).filter(Student.school_branch_id==request.args.get("branch_id")).limit(5)

    studentList = []
    for student in students:
        tokens = student.name.split(" ")
        tokens.append(student.name)
        studentList.append({
            "name" : student.name,
            "student_id" : student.student_id,
            "class_student_id" : student.class_student_id,
            "id" : student.id,
            "tokens" : tokens,
            "value" : student.name
        })
    return json.dumps(studentList)


@application.route("/schools")
def schools():
    if request.args.get("suggest") == False or request.args.get("suggest") == None:
        schools = db.session.query(School).all()
    else:
        searchstring = request.args.get("suggest") + '%'
        schools = db.session.query(School).filter(School.name.like(searchstring)).limit(5)

    schoolList = []
    for school in schools:
        schoolList.append({
            "name" : school.name,
            "branch_id" : school.school_branch_id,
            "school_id" : school.school_id,
            "id" : school.id,
            "tokens" : [school.name],
            "value" : school.name
        })
    return json.dumps(schoolList)

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
                }), 404
        else:
            return json.dumps({
                "status" : "error",
                "error" : "No access token fetched",
                "error_code" : "403",
                "error_message" : data.error
            }), 403
    else:
        return json.dumps({
            "status" : "error",
            "error" : request.args.get("error"),
            "error_code" : 500,
        }), 500

# Run the app/server
if __name__ == '__main__':
    application.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )