#######################################################
# IMPORT DEPENDENCIES
#######################################################
import requests
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required, UserMixin, LoginManager, current_user
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
import time

TIMEFMT = "%a, %d %b %Y %H:%M:%S +0000"

db = SQLAlchemy()

def create_app():
    # Base app configuration
    #
    app = Flask(__name__)
    app.config.from_pyfile('.env.py', silent=True)

    # Basic DB configuration
    #
    db.init_app(app)
    db.create_all(app=app)

    # Configure our login manager for the app
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    # Define our method for loading current_user data
    #
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()

#  PostgresSQL/SQLAlchemy classes for objects.
