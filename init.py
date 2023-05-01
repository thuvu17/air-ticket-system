# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       db='air-ticket-reservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# HELLO
app.route('/')
def hello():
    return render_template('index.html')


# GOODBYE
app.route('/goodbye')
def goodbye():
    return redirect('/')


# LOGOUT STAFF
@app.route('/logoutStaff')
def logoutStaff():
    session.pop('username')
    return redirect('/goodbye')


# LOGOUT CUSTOMER
@app.route('/logoutCust')
def logoutCust():
    session.pop('email')
    return redirect('/goodbye')


# LOGIN STAFF
@app.route('/loginStaff')
def loginStaff():
    return render_template('loginStaff.html')

# LOGIN CUSTOMER
@app.route('/loginCust')
def loginCust():
    return render_template('loginCust.html')


# REGISTER CUSTOMER
@app.route('/registerCust')
def registerCust():
    return render_template('registerCust.html')

# REGISTER STAFF
@app.route('/registerStaff')
def registerStaff():
    return render_template('registerStaff.html')


# LOGIN AUTHENTICATION STAFF
@app.route('/loginAuthStaff', methods=['GET', 'POST'])
def loginAuthStaff():
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
        return redirect(url_for('homeStaff'))
    else:
        # returns an error message to the html page
        error = 'Invalid username or password'
        return render_template('loginStaff.html', error=error)


# LOGIN AUTHENTICATION CUSTOMER
@app.route('/loginAuthCust', methods=['GET', 'POST'])
def loginAuthCust():
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
        return redirect(url_for('homeCust'))
    else:
        # returns an error message to the html page
        error = 'Invalid email or password'
        return render_template('loginCust.html', error=error)


# REGISTER AUTHENTICATION CUSTOMER
@app.route('/registerAuthCust', methods=['GET', 'POST'])
def registerAuthCust():
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
        return render_template('registerCust.html', error=error)
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
@app.route('/registerAuthStaff', methods=['GET', 'POST'])
def registerAuthStaff():
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
        return render_template('registerStaff.html', error=error)
    else:
        # insert into airline_staff
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, airline_name, password,
                       first_name, last_name, date_of_birth))
        conn.commit()
        phone_nums = phone_num.split('%2C')
        emails = email.split('%2C')
        # insert all phone numbers into staff_phone
        for num in phone_nums:
            ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
            cursor.execute(ins, (username, num))
            conn.commit()
        # insert all email into staff_email
        for emailAddr in emails:
            ins = 'INSERT INTO staff_email VALUES(%s, %s)'
            cursor.execute(ins, (username, emailAddr))
            conn.commit()
        cursor.close()
        return render_template('index.html')
