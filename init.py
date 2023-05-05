# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime, timedelta
import pymysql.cursors
import hashlib
# Import use cases
import cust_use_cases
import staff_use_cases
from staff_use_cases import get_flight_info
from setup import app, conn



# HELLO
@app.route('/')
def hello():
    return render_template('index.html')


# LOGOUT STAFF
@app.route('/logout_staff')
def lougout_staff():
    session.pop('username')
    return redirect('/login_staff')

# LOGOUT CUSTOMER
@app.route('/logout_cust')
def logout_cust():
    session.pop('email')
    return redirect('/login_cust')


# LOGIN STAFF
@app.route('/login_staff')
def login_staff():
    return render_template('login_staff.html')

# LOGIN CUSTOMER
@app.route('/login_cust')
def login_cust():
    return render_template('login_cust.html')


# REGISTER CUSTOMER
@app.route('/register_cust')
def register_cust():
    return render_template('register_cust.html')

# REGISTER STAFF
@app.route('/register_staff')
def register_staff():
    cursor = conn.cursor()
    # get all airlines for staff to select from
    get_airlines = 'SELECT airline_name FROM airline'
    cursor.execute(get_airlines)
    airlines = cursor.fetchall()
    return render_template('register_staff.html', airlines=airlines)


# LOGIN AUTHENTICATION STAFF
@app.route('/login_auth_staff', methods=['POST'])
def login_auth_staff():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    encrypted = hashlib.md5(password)
    # executes query
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
    cursor.execute(query, (username, encrypted))
    # stores the results in a variable
    data = cursor.fetchone()
    cursor.close()
    error = None
    if data:
        # creates a session for the the user
        session['username'] = username
        return redirect(url_for('home_staff'))
    else:
        # returns an error message to the html page
        error = 'Invalid username or password'
        return render_template('login_staff.html', error=error)


# LOGIN AUTHENTICATION CUSTOMER
@app.route('/login_auth_cust', methods=['POST'])
def login_auth_cust():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    encrypted = hashlib.md5(password)
    # executes query
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s and password = %s'
    cursor.execute(query, (email, encrypted))
    # stores the results in a variable
    data = cursor.fetchone()
    cursor.close()
    error = None
    if data:
        # creates a session for the the user
        session['email'] = email
        return redirect(url_for('home_cust'))
    else:
        # returns an error message to the html page
        error = 'Invalid email or password'
        return render_template('login_cust.html', error=error)


# REGISTER AUTHENTICATION CUSTOMER
@app.route('/register_auth_cust', methods=['POST'])
def register_auth_cust():
    # grabs information from the forms
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    passport_num = request.form['passport_num']
    passport_exp = request.form['passport_exp']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']
    email = request.form['email']
    password = request.form['password']
    phone_num = request.form['phone_num']
    building_num = request.form['building_num']
    street = request.form['street']
    apt_num = request.form['apt_num']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zip_code']

    # cursor used to send queries
    cursor = conn.cursor()
    # check if account existed
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()
    error = None
    if data:
        # If the previous query returns data, then account exists
        error = "This account already exists"
        return render_template('register_cust.html', error=error)
    else:
        encrypted = hashlib.md5(password)
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, encrypted, first_name, last_name, building_num,
                             street, apt_num, city, state, zip_code, passport_num, passport_exp,
                             passport_country, date_of_birth))
        conn.commit()
        # add multiple phone numbers
        phone_nums = phone_num.replace(' ', '').split(',')
        for num in phone_nums:
            ins = 'INSERT INTO cust_contact VALUES(%s, %s)'
            cursor.execute(ins, (num, email))
            conn.commit()
        cursor.close()
        return render_template('index.html')


# REGISTER AUTHENTICATION STAFF
@app.route('/register_auth_staff', methods=['POST'])
def register_auth_staff():
    # grabs information from the forms
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    airline_name = request.form['airline_name']
    phone_num = request.form['phone_num']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    # cursor used to send queries
    cursor = conn.cursor()
    # check if account existed
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    error = None
    if data:
        # If the previous query returns data, then account exists
        error = "This account already exists"
        return render_template('register_staff.html', error=error)
    else:
        # insert into airline_staff
        encrypted = hashlib.md5(password)
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, airline_name, encrypted,
                       first_name, last_name, date_of_birth))
        conn.commit()
        phone_nums = phone_num.replace(' ', '').split(',')
        emails = email.replace(' ', '').split(',')
        # insert all phone numbers into staff_phone
        for num in phone_nums:
            ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
            cursor.execute(ins, (username, num))
            conn.commit()
        # insert all email into staff_email
        for email_addr in emails:
            ins = 'INSERT INTO staff_email VALUES(%s, %s)'
            cursor.execute(ins, (username, email_addr))
            conn.commit()
        cursor.close()
        return render_template('index.html')



# VIEW PUBLIC INFO
@app.route('/search_flight', methods=['GET', 'POST'])
def search_flight():
    if request.method == 'POST':
        cursor = conn.cursor()
        # get search info
        one_or_round = request.form['one_or_round']
        source_city = request.form['source_city']
        source_airport = request.form['source_airport']
        dest_city = request.form['dest_city']
        dest_airport = request.form['dest_airport']
        dept_date = request.form['dept_date']
        # condition for query
        condition = "dept.city = '{}' and dept.name = '{}' and \
                arr.city = '{}' and arr.name = '{}' and date(dept_datetime) = '{}'"
        # if one way
        if one_or_round == "one":
            one_condition = condition.format(source_city, source_airport, dest_city, dest_airport, dept_date)
            one_flights = get_flight_info(cursor, one_condition)
            cursor.close()
            return render_template('one_way_result.html', one_flights=one_flights)
        # if round trip
        else:
            return_date = request.form['return_date']
            forward_condition = condition.format(source_city, source_airport, dest_city, dest_airport, dept_date)
            return_condition = condition.format(dest_city, dest_airport, source_city, source_airport, return_date)
            forward_flights = get_flight_info(cursor, forward_condition)
            return_flights = get_flight_info(cursor, return_condition)
            cursor.close()
            return render_template('round_result.html', forward_flights=forward_flights, return_flights=return_flights)
    else:
        return render_template('search_flight.html')