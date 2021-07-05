DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS ground_queries;
DROP TABLE IF EXISTS air_queries;
DROP TABLE IF EXISTS offsets;

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