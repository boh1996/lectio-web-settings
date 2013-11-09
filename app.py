from flask import Flask
import config
from flask.ext.sqlalchemy import SQLAlchemy

# App settings
application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = '%s://%s:%s@%s/%s?charset=utf8' % (config.database_system, config.db_username, config.db_password, config.db_host, config.db_schema)
db = SQLAlchemy(application)