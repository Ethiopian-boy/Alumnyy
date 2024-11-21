from flask import Flask, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.utils import secure_filename
import os
import urllib.request
from flask_login import login_required, current_user

db = SQLAlchemy()

UPLOAD_FOLDER = './static/pp'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'SE Pot!!!**%%##WooJ'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/alumnyy'
    db.init_app(app)
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import user, post

    create_database(app)

    # Manage logins
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return user.query.get(int(id))

    return app

def create_database(app):
    with app.app_context():
        db.create_all()
        print ("Database created! ") 