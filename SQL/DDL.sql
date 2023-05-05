CREATE TABLE airline (
    airline_name VARCHAR(20) PRIMARY KEY
); 
    
CREATE TABLE airplane (
    airline_name VARCHAR(20),
    plane_id CHAR(5),
    seats INT,
    company VARCHAR(20),
    manu_date DATE,
    PRIMARY KEY(airline_name, plane_id),
    FOREIGN KEY(airline_name) REFERENCES airline(airline_name)
); 
    
CREATE TABLE airline_staff (
    username VARCHAR(10) PRIMARY KEY,
    airline_name VARCHAR(20),
    `password` VARCHAR(200),
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    date_of_birth DATE,
    FOREIGN KEY(airline_name) REFERENCES airline(airline_name)
);
    
CREATE TABLE staff_email (
    username VARCHAR(10),
    email VARCHAR(20),
    PRIMARY KEY(username, email),
    FOREIGN KEY(username) REFERENCES airline_staff(username)
);
    
CREATE TABLE staff_phone (
    username VARCHAR(10),
    phone_num VARCHAR(10),
    PRIMARY KEY(username, phone_num),
    FOREIGN KEY(username) REFERENCES airline_staff(username)
);
    
CREATE TABLE airport (
    airport_code CHAR(5) PRIMARY KEY,
    name VARCHAR(20),
    city VARCHAR(20),
    country VARCHAR(20),
    `type` ENUM('international', 'domestic', 'both')
);

CREATE TABLE flight (
    airline_name VARCHAR(20),
    flight_num CHAR(5),
    dept_datetime DATETIME,
    plane_airline VARCHAR(20),
    plane_id CHAR(5),
    arrive_datetime DATETIME,
    arrive_airport CHAR(5),
    dept_airport CHAR(5),
    `status` ENUM('on-time', 'delayed', 'arrived', 'diverted', 'cancelled', 'completed', 'boarding', 'in-flight'),
    base_price NUMERIC(8, 2) ,
    PRIMARY KEY(airline_name, flight_num, dept_datetime),
    FOREIGN KEY(arrive_airport) REFERENCES airport(airport_code),
    FOREIGN KEY(dept_airport) REFERENCES airport(airport_code),
    FOREIGN KEY(airline_name) REFERENCES airline(airline_name),
    FOREIGN KEY(plane_airline, plane_id) REFERENCES airplane(airline_name, plane_id)
);

CREATE TABLE ticket (
    ticket_id CHAR(5) PRIMARY KEY,
    airline_name VARCHAR(20),
    flight_num CHAR(5),
    dept_datetime DATETIME,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    date_of_birth DATE,
    FOREIGN KEY(airline_name, flight_num, dept_datetime) REFERENCES flight(airline_name, flight_num, dept_datetime)
);

CREATE TABLE payment_info (
    card_num VARCHAR(16) PRIMARY KEY,
    card_type ENUM('credit', 'debit'),
    card_name VARCHAR(20),
    exp_date DATE
);

CREATE TABLE customer (
    email VARCHAR(20) PRIMARY KEY,
    `password` VARCHAR(200),
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    building_num VARCHAR(5),
    street VARCHAR(20),
    apt_num VARCHAR(5),
    city VARCHAR(20),
    STATE VARCHAR(20),
    zip_code CHAR(5),
    passport_num VARCHAR(10),
    passport_exp DATE,
    passport_country VARCHAR(20),
    date_of_birth DATE
);

CREATE TABLE purchases (
    ticket_id CHAR(5),
    card_num VARCHAR(16),
    email VARCHAR(20),
    date_time DATETIME,
    calc_price FLOAT,
    rating NUMERIC(2, 1),
    `comment` VARCHAR(100),
    PRIMARY KEY(ticket_id, card_num, email),
    FOREIGN KEY(ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY(card_num) REFERENCES payment_info(card_num),
    FOREIGN KEY(email) REFERENCES customer(email)
);

CREATE TABLE cust_contact (
    phone_num VARCHAR(10),
    email VARCHAR(20),
    PRIMARY KEY(phone_num, email),
    FOREIGN KEY(email) REFERENCES customer(email)
);