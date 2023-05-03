# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime, timedelta
import pymysql.cursors

# include customer use cases
import cust_use_cases

# Initialize the app from Flask
app = Flask(__name__)


# Configure MySQL
conn = pymysql.connect(host='localhost',
                       port= 8889,
                       user='root',
                       password='root',
                       db='air_ticket_reservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# Secret key
app.secret_key = 'this is the secret key'

# HELLO
@app.route('/')
def hello():
    return render_template('index.html')


# LOGOUT STAFF
@app.route('/lougout_staff')
def lougout_staff():
    session.pop('username')
    return redirect(url_for('/'))

# LOGOUT CUSTOMER
@app.route('/logout_cust')
def logout_cust():
    session.pop('email')
    return redirect(url_for('/'))


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
    return render_template('register_staff.html')


# LOGIN AUTHENTICATION STAFF
@app.route('/login_auth_staff', methods=['GET', 'POST'])
def login_auth_staff():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    # executes query
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
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
@app.route('/login_auth_cust', methods=['GET', 'POST'])
def login_auth_cust():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    # executes query
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s and password = %s'
    cursor.execute(query, (email, password))
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
@app.route('/register_auth_cust', methods=['GET', 'POST'])
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
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, password, first_name, last_name, building_num,
                             street, apt_num, city, state, zip_code, passport_num, passport_exp,
                             passport_country, date_of_birth))
        conn.commit()
        # add multiple phone numbers
        phone_nums = phone_num.split('%2C')
        for num in phone_nums:
            ins = 'INSERT INTO cust_contact VALUES(%s, %s)'
            cursor.execute(ins, (num, email))
            conn.commit()
        cursor.close()
        return render_template('index.html')


# REGISTER AUTHENTICATION STAFF
@app.route('/register_auth_staff', methods=['GET', 'POST'])
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
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, airline_name, password,
                       first_name, last_name, date_of_birth))
        conn.commit()
        phone_nums = phone_num.split('%2C')
        emails = email.split('%2C')
        # TODO: haven't tested
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

query_for_search_flight = 'SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, arrive_datetime \
    FROM (SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, arrive_datetime \
        FROM flight natural join airport natural join airplane WHERE date(dept_datetime) = "{}" and \
            arrive_airport = airport_code and name = "{}" and city = "{}") sub natural join airport \
                WHERE dept_airport = airport_code and name = "{}" and city = "{}"'

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
        # if one way
        if one_or_round == "one":
            search = query_for_search_flight.format(dept_date, dest_airport, dest_city, source_airport, source_city)
            cursor.execute(search)
            one_flights = cursor.fetchall()
            cursor.close()
            return render_template('one_way_result.html', one_flights=one_flights)
        # if round trip
        else:
            return_date = request.form['return_date']
            search_forward = query_for_search_flight.format(dept_date, dest_airport, dest_city, source_airport, source_city)
            search_return = query_for_search_flight.format(return_date, source_airport, source_city, dest_airport, dest_city)
            # search forward flights
            cursor.execute(search_forward)
            forward_flights = cursor.fetchall()
            # search return flights
            cursor.execute(search_return)
            return_flights = cursor.fetchall()
            cursor.close()
            return render_template('round_result.html', forward_flights=forward_flights, return_flights=return_flights)
    else:
        return render_template('search_flight.html')