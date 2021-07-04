DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS ground_queries;
DROP TABLE IF EXISTS air_queries;

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
    offset_zip TEXT NOT NULL,
    offset_type TEXT NOT NULL,
    results TEXT NOT NULL
);

CREATE TABLE air_queries (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email TEXT NOT NULL,
    airport_list TEXT NOT NULL,
    offset_zip TEXT NOT NULL,
    offset_type TEXT NOT NULL,
    results TEXT NOT NULL
);

