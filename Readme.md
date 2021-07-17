# Overview
A web application to offset ground or air transportation. Enter your mileage and miles per gallon, and zip code. This will then display a list of offsets and more details about them. A user can then go to those sites and purchase to drawdown carbon and mitigate their personal carbon footprint. On the "list offsets" page you can filter by the type of offset you would like (for example, solar, wind, forest management, etc).

This could be used as a personal application or for B2B purposes, especially of an organization  working to integrate  practical solutions to the effects of climate change. 

---
# Technologies Used
- Python
- Jinja (template engine)
- Flask
- SQL Alchemy
- POSTGRESQL
- JavaScript
- CSS
- HTML

---
# Models
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    passwd TEXT NOT NULL,
    token TEXT NOT NULL
);

CREATE TABLE ground_queries (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email TEXT NOT NULL,
    miles FLOAT NOT NULL,
    mpg FLOAT NOT NULL,
    city TEXT NOT NULL,
    results TEXT NOT NULL
);

CREATE TABLE air_queries (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email TEXT NOT NULL,
    airport_list TEXT NOT NULL,
    results TEXT NOT NULL
);

CREATE TABLE offsets (
    id SERIAL PRIMARY KEY,
    offset_name TEXT NOT NULL,
    slug TEXT NOT NULL,
    city TEXT NOT NULL,
    province TEXT NOT NULL,
    country TEXT NOT NULL,
    offset_type TEXT NOT NULL,
    total_capacity TEXT NOT NULL,
    avail_capacity TEXT NOT NULL,
    details TEXT NOT NULL,
    pretty_url TEXT NOT NULL
);

# Installation

1. It is strongly recommended that a virtual environment for Python is used for all applications.  To create and activate an envrionment:

        python3 -m venv venv
        source bin/venv/activate

2. Install the Python prerequisites listed in the "requirements.txt" file

        pip install -r requirements.txt

3. Initialize the back-end Postgress database:

        psql -U {database user} {database name - optional} -f postgress_schema.sql

4. Update the .env.py file, which includes configuration information for the Flask application.  Basic content is:

        DEBUG = True  # Turns on debugging features in Flask
        APP = 'app'   # The class instance of the Flask Application

        CLOVERLY_PUBLIC_KEY = 'Bearer public_key:xxxxxxxxx'   # Public key for Cloverly                                              access
        SECRET_KEY = 'asdfr437f8adsf7FD&7fd6sf'               # For Flask security         

        SQLALCHEMY_TRACK_MODIFICATIONS = False  
        SQLALCHEMY_DATABASE_URI = 'postgresql://{hostname}/{db_name}?user={username}&password={password}'

5. Run the Flask application

        export FLASK_APP=app
        flask run

6. Note the port number given on stdout, default port is 5000
7. Connect browser to http://localhost:5000/


# Usage
1. Create a new user by selecting the "New User" link from the navigation bar
2. Enter name, email, and desired password
3. When user is created, note the token string that is displayed - this can be used in making direct API calls to the app
4. Select "Login" from the navigation bar and enter credentials
5. The dashboard is initially blank for a new user
6. To make a Ground or Air query, select the appropriate task from the navigation bar
   1. Enter required fields
   2. Select "Submit"
   3. An estimate is displayed for this travel
   4. To view appropriate offsets for this estimate, select "Show Offsets"
   5. Select individual offsets to explore possibilities
7. Return to the Home task on the navigation bar
8. Note that estimates now appear in the dashboard
9. Select Edit to edit an estimate
10. Select Delete to delete an estimate
11. Select Logout to end the CarbonProject session


# Deployment

1. Can be deployed as a single application or split-stack which separates the DB and Application layers
2. If split, modify the SQLALCHEMY_DATABASE_URI and add other validation (app token, etc.) to secure