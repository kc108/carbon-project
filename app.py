
# IMPORT DEPENDENCIES
import requests
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required, UserMixin, LoginManager, current_user
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
import time
import os


TIMEFMT = "%a, %d %b %Y %H:%M:%S +0000"

# CREATE INSTANCE FOR SESSION to connect to DB
db = SQLAlchemy()

# Instantiates the app to use Flask and loads configuration
def create_app():
    # Base app configuration
    #
    app = Flask(__name__, static_folder="static")

    use_env = os.environ.get("USEENV")
    if(use_env):
        DEBUG = os.environ.get("DEBUG")
        APP = os.environ.get("APP")
        app.config["CLOVERLY_PUBLIC_KEY"] = os.environ.get("CLOVERLY_PUBLIC_KEY")
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    else:
        # silent=true hides debugging info to hide keys
        app.config.from_pyfile('.env.py', silent=True)

    # Basic DB configuration - uses config for postgresql
    db.init_app(app)
    db.create_all(app=app)

    app.secret_key = "super secret key"

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

# instantiating flask app
app = create_app()

#  PostgresSQL/SQLAlchemy classes for objects.


# Class to hold Ground estimates
class GroundQuery(db.Model):
    __tablename__ = 'ground_queries'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    miles = db.Column(db.Float, nullable=False)
    mpg = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(), nullable=False)
    results = db.Column(db.String(), nullable=False)

    # constructor function stores these in the instance variable related to fields
    def __init__(self, email, miles, mpg, city, results):
        self.created = time.strftime(TIMEFMT, time.gmtime())
        self.email = email
        self.miles = miles
        self.mpg = mpg
        self.city = city
        self.results = results


# Class to hold Air estimates
class AirQuery(db.Model):
    __tablename__ = 'air_queries'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    airport_list = db.Column(db.String(), nullable=False)
    results = db.Column(db.String(), nullable=False)

    def __init__(self, email, airport_list, results):
        self.created = time.strftime(TIMEFMT, time.gmtime())
        self.email = email
        self.airport_list = airport_list
        self.results = results

    # helps with debug
    def __repr__(self):
        return '<id {}>'.format(self.id)

    #
    def list_airports(self):
        airports = self.airport_list[1:-1].split(',')
        airport_list = [airport.upper() for airport in airports]
        return ' ->'.join(airport_list)

    def text_airports(self):
        airports = self.airport_list[1:-1].split(',')
        airport_list = [airport.upper() for airport in airports]
        return ', '.join(airport_list)


# Class to hold User data
# UserMixin used for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(), nullable=False)
    passwd = db.Column(db.String(), nullable=False)
    token = db.Column(db.String(), nullable=False)


    def __init__(self, full_name, email, password, token):
        self.created = time.strftime(TIMEFMT, time.gmtime())
        self.full_name = full_name
        self.email = email
        self.passwd = generate_password_hash(password)
        self.token = token

    # debugging purposes
    def __repr__(self):
        return '<id {}>'.format(self.id)


# Class to hold Offset data
class Offset(db.Model):
    __tablename__ = 'offsets'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(), nullable=False)
    offset_name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    province = db.Column(db.String(), nullable=False)
    country = db.Column(db.String(), nullable=False)
    offset_type = db.Column(db.String(), nullable=False)
    total_capacity = db.Column(db.String(), nullable=False)
    avail_capacity = db.Column(db.String(), nullable=False)
    details = db.Column(db.String(), nullable=False)
    pretty_url = db.Column(db.String(), nullable=False)

    def __init__(self, offset_name, slug, city, province, country, offset_type,
                 total_capacity, avail_capacity, details, pretty_url):

        self.offset_name = offset_name
        self.slug = slug
        self.city = city
        self.province = province
        self.country = country
        self.offset_type = offset_type
        self.total_capacity = total_capacity
        self.avail_capacity = avail_capacity
        self.details = details
        self.pretty_url = pretty_url


# "Internal" functions used by the Flask routes and such
#

# Accepts a token from an API call (in data JSON), and searches
# User database for a matching token.  Return True if token found
def validate_token(token):
    success = User.query.filter_by(token = token).first()
    if success is None:
        return False
    return success


# Retreive impact estimate from Cloverly API based on user input
# Return JSON received for later processing
def api_ground_transport(miles, mpg):
    url = 'https://api.cloverly.com/2019-03-beta/estimates/vehicle'
    key = app.config['CLOVERLY_PUBLIC_KEY']
    headers = {'Content-type': 'application/json',
               'Authorization': key}
    data = {"distance":{"value":miles,"units":"miles"},"fuel_efficiency":{"value":mpg,"units":"mpg","of":"gasoline"}}
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()


# Retreive impact estimate from Cloverly API based on user input
# Return JSON received for later processing
def api_air_transport(airports):
    url = 'https://api.cloverly.com/2019-03-beta/estimates/flight'
    key = app.config['CLOVERLY_PUBLIC_KEY']
    headers = {'Content-type': 'application/json',
               'Authorization': key}
    data = {"airports":airports}
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()


# Retreive potential offstes from Cloverly API 
# Store in DB for further use and filtering
def api_get_offsets():
    url = 'https://api.cloverly.com/2019-03-beta/offsets'
    key = app.config['CLOVERLY_PUBLIC_KEY']
    headers = {'Content-type': 'application/json',
           'Authorization': key}
    # Offset.query.delete()
    
    offsets = requests.get(url, headers=headers)
    for offset in offsets.json():
        row = Offset(offset['name'], offset['slug'], offset['city'],
                     offset['province'], offset['country'],
                     offset['offset_type'], offset['total_capacity'], 
                     offset['available_carbon_in_kg'], offset['technical_details'], 
                     offset['pretty_url'])
        db.session.add(row)
        db.session.commit

# test for zip code ?
def api_list_offsets_by_zip(zipcode):
    url = 'https://api.cloverly.com/2019-03-beta/purchases/electricity'
    key = app.config['CLOVERLY_PUBLIC_KEY']
    headers = {'Content-type': 'application/json',
           'Authorization': key}
    data = '{"energy":{"value":1,"units":"kwh"},"offset_match":{"type":"solar","location":{"postal_code":"94043","country":"US"}}}'
    r = requests.post(url, headers=headers, data=data)
    return r.json()


# Retreive specific offset details from Cloverly API
# based on SLUG ID
# Return JSON received for later processing
def api_get_offset_by_slug(slug):
    url = 'https://api.cloverly.com/2019-03-beta/offsets/{}'.format(slug)
    key = app.config['CLOVERLY_PUBLIC_KEY']
    headers = {'Content-type': 'application/json',
            'Authorization': key}
    r = requests.get(url, headers=headers)
    return r.json()


# Look up a ground Query object from the database and return
def get_ground_query(query_id):
    query = GroundQuery.query.get(query_id)
    if query is None:
        abort(404)
    return query


# Look up an air Query object from the database and return
def get_air_query(query_id):
    query = AirQuery.query.get(query_id)
    if query is None:
        abort(404)
    return query


# Flask routes (web pages) that are available BEFORE LOGIN is completed
# 

# The main route for the application.  Displays a blank page with 
# links to "New User" and "Login" pages
@app.route('/')
def index():
    if current_user:
        return redirect(url_for('home'))
    return render_template('nologin_index.html')


# The Login page for the app.  Displays a simple form for input
# and attempts to login in by checking inputted password (hashed)
# against User database.  Redirects to /home if successful
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        if not (email and password):
            flash('Email and password are required!!')
        else:
            if request.form.get('remember') == 'on':
                rem = True
            else:
                rem = False
            user = User.query.filter_by(email=email).first()
            if not check_password_hash(user.passwd, password):
                flash('Invalid login')
                return redirect(url_for('login'))
            login_user(user, remember=rem)
            return redirect(url_for('home'))
        return render_template('login.html')
    if request.method == 'GET':
        return render_template('login.html')


# User registration page.  Accepts input, checks for duplicate email
# registrations, and creates a new user.  Displays a banner with the 
# JWT generated for that user.
@app.route('/create_user', methods=('GET', 'POST'))
def create_user():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        passwd = request.form.get('pass')
        token = jwt.encode({full_name: email}, email, algorithm="HS256")

        if not (email and full_name):
            flash('Name and email are required!')
        elif User.query.filter_by(email=email).first():
            flash('That email is already registered')
        else:
            new_user = User(full_name, email, passwd, token)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('create_user.html')


# Flask routes (web pages) that are accessible only AFTER LOGIN
#

# The main page for logged-in users.  Displays a dashboard of previous estimates,
# allows for editing/deleting those estimates, and displays the full set of actions
# on the navigation bar
@app.route('/home')
@login_required
def home():
    ground_queries = GroundQuery.query.filter_by(email = current_user.email)
    air_queries = AirQuery.query.all()
    return render_template('home.html', user=current_user, ground_queries=ground_queries[::-1], air_queries=air_queries[::-1])


# Logs user out of session and returns to login page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Retrieves and displays a previously submitted ground esitmate.
# Retreives estimate details from database and re-encodes to JSON
# for easier parsing on the display page
@app.route('/ground/<int:query_id>')
@login_required
def show_ground_query(query_id):
    query = get_ground_query(query_id)
    result_json = json.loads(query.results)
    return render_template('show_ground_query.html', query=query, result=result_json)


# Retrieves and displays a previously submitted air esitmate.
# Retreives estimate details from database and re-encodes to JSON
# for easier parsing on the display page
@app.route('/air/<int:query_id>')
@login_required
def show_air_query(query_id):
    query = get_air_query(query_id)
    result_json = json.loads(query.results)
    return render_template('show_air_query.html', query=query, result=result_json)


# Displays a specific offset opportunity based on the SLUG ID provided
@app.route('/offset/<string:slug>')
@login_required
def show_offset(slug):
    slug = api_get_offset_by_slug(slug)
    return render_template('show_offset.html', slug=slug)


# Creates a ground transportation estimate based on users input.
# Stores the query and results in the database
@app.route('/ground_query', methods=('GET', 'POST'))
@login_required
def ground_query():
    if request.method == 'POST':
        miles = request.form['miles']
        mpg = request.form['mpg']
        city = request.form['city']

        if not (miles and mpg): 
            flash('Miles and MPG are required!')
        else:
            results = api_ground_transport(miles, mpg)
            new_query = GroundQuery(
                current_user.email, miles, mpg, city, json.dumps(results))
            db.session.add(new_query)
            db.session.commit()
        return redirect('/ground/' + str(new_query.id))
    return render_template('ground_query.html')


# Creates an air transportation estimate based on users input.
# Stores the query and results in the database
@app.route('/air_query', methods=('GET', 'POST'))
@login_required
def air_query():
    if request.method == 'POST':
        airport_text = request.form['airports'].replace(" ","")
        airports = airport_text.split(',')

        if not airports:
            flash('Airport list and an access token are required!')
        else:
            results = api_air_transport(airports)
            new_query = AirQuery(current_user.email,
                                    airports, json.dumps(results))
            db.session.add(new_query)
            db.session.commit()
        return redirect('/air/' + str(new_query.id))
    return render_template('air_query.html')


# Using an API, retreives a list of potential offsets from Cloverly 
# and displays them for user review
@app.route('/list_offset', methods=['GET', 'POST'])
def list_offset():
    api_get_offsets()
    offsets = Offset.query.all()
    if request.method == 'POST' and request.form['offset_type'] != "All":
        offsets = [off for off in offsets if off.offset_type == request.form['offset_type']]
    return render_template('offsets.html', offsets=offsets)

# form element to get nearest one by zip
# @app.route('/list_offset/<int:zipcode>', methods=['GET', 'POST'])
# def list_offset(zipcode):
#     offsets = api_list_offsets_by_zip(zipcode)
#     for off in offsets.get('offset'):
#         flash(off.name)
#     return render_template('offsets.html', offsets=offsets)


# Deletes a previously stored ground query
@app.route('/<int:id>/delete_ground_query', methods=('POST', 'GET'))
@login_required
def delete_ground_query(id):
    delme = GroundQuery.query.get(id)
    db.session.delete(delme)
    db.session.commit()
    flash('Ground Query ID: "{}" was successfully deleted!'.format(id))
    return redirect(url_for('home'))


# Deletes a previously stored air query
@app.route('/<int:id>/delete_air_query', methods=('POST', 'GET'))
@login_required
def delete_air_query(id):
    delme = AirQuery.query.get(id)
    db.session.delete(delme)
    db.session.commit()
    flash('Air Query ID: "{}" was successfully deleted!'.format(id))
    return redirect(url_for('home'))


# Edits a previously stored ground query.  Replaces the previous
# query details with the updated parameters and results from
# the Cloverly API
@app.route('/edit_ground_query/<int:id>', methods=('GET', 'POST'))
def edit_ground_query(id):
    post = get_ground_query(id)

    if request.method == 'POST':
        miles = request.form['miles']
        mpg = request.form['mpg']
        city = request.form['city']

        if not (miles and mpg):
            flash('Miles and MPG are required!')
        else:
            results = api_ground_transport(miles, mpg)
            new_query = GroundQuery(
                current_user.full_name, miles, mpg, city, json.dumps(results))
            old_query = GroundQuery.query.get(id)
            old_query.miles = new_query.miles
            old_query.mpg = new_query.mpg
            old_query.city = new_query.city
            old_query.results = new_query.results
            db.session.commit()
        return redirect('/ground/' + str(old_query.id))

    return render_template('edit_ground_query.html', post=post)


# Edits a previously stored air query.  Replaces the previous
# query details with the updated parameters and results from
# the Cloverly API
@app.route('/edit_air_query/<int:id>', methods=('GET', 'POST'))
def edit_air_query(id):
    post = get_air_query(id)

    if request.method == 'POST':
        airport_text = request.form['airports'].replace(" ", "")
        airports = airport_text.split(',')

        if not airports:
            flash('Airport list and an access token are required!')
        else:
            results = api_air_transport(airports)
            new_query = AirQuery(current_user.full_name,
                                 airports, json.dumps(results))
            old_query = AirQuery.query.get(id)
            old_query.airport_list = new_query.airport_list
            old_query.results = new_query.results
            db.session.commit()
        return redirect('/air/' + str(old_query.id))

    return render_template('edit_air_query.html', post=post)


# Direct APIs for users
#

# Receives a JSON payload from a client.  Validates the token provided
# matches a registered user, and creates the estimate which is stored
# in the database for later use by that user.
# this is for the user facing API, AAU have to give miles, mpg and token and returns the json results from cloverly
@app.route('/api/ground_query', methods=('POST', 'GET'))
def api_ground_query():
    request_data = json.loads(request.data)
    user = validate_token(request_data['token'])
    if user:
        email = user.email
        miles = request_data['miles']
        mpg = request_data['mpg']
        results = api_ground_query(miles, mpg)
        new_query = GroundQuery(email, miles, mpg, json.dumps(results))
        db.session.add(new_query)
        db.session.commit()
        return results  
    else:
        return "Invalid Token"


