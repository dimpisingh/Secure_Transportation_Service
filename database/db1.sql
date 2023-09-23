-- Database: ridesharing

-- DROP DATABASE IF EXISTS ridesharing;

CREATE DATABASE ridesharing
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_India.1252'
    LC_CTYPE = 'English_India.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Create a schema for user-related objects
CREATE SCHEMA user_schema;

-- Create a schema for ride-related objects
CREATE SCHEMA ride_schema;

-- Create a table for user data within the user_schema
DROP TABLE IF EXISTS users;
CREATE TABLE user_schema.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP DEFAULT current_timestamp
);

-- Create a table for ride data within the ride_schema
DROP TABLE IF EXISTS rides;
CREATE TABLE ride_schema.rides (
    ride_id SERIAL PRIMARY KEY,
    driver_id INT REFERENCES user_schema.users(user_id),
    start_location VARCHAR(255) NOT NULL,
    end_location VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    available_seats INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT valid_seats CHECK (available_seats >= 0),
    CONSTRAINT valid_time CHECK (start_time < end_time)
);
