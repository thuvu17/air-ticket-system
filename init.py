#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='blog',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for login
@app.route('/loginStaff')
def loginStaff():
	return render_template('loginStaff.html')

@app.route('/loginCust')
def loginCust():
	return render_template('loginCust.html')

#Define route for customer register
@app.route('/registerCust')
def registerCust():
	return render_template('registerCust.html')

#Define route for staff register
@app.route('/registerStaff')
def registerStaff():
	return render_template('registerStaff.html')


#Authenticates the login for staff
@app.route('/loginAuthStaff', methods=['GET', 'POST'])
def loginAuthStaff():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	#executes query
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid username or password'
		return render_template('loginStaff.html', error=error)


#Authenticates the login for customer
@app.route('/loginAuthCust', methods=['GET', 'POST'])
def loginAuthCust():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	#executes query
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid username or password'
		return render_template('loginCust.html', error=error)


#Authenticates customer register
@app.route('/registerAuthCust', methods=['GET', 'POST'])
def registerAuthCust():
	#grabs information from the forms
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

	#cursor used to send queries
    cursor = conn.cursor()
	#executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
	#stores the results in a variable
    data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
		#If the previous query returns data, then account exists
        error = "This account already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, password, first_name, last_name, building_num, \
			street, apt_num, city, state, zip_code, passport_num, passport_exp, \
		    passport_country, date_of_birth))
        conn.commit()
        phone_nums = phone_num.split('%2C')
        for num in phone_nums:
            ins = 'INSERT INTO cust_contact VALUES(%s, %s)'
            cursor.execute(ins, (num, email))
            conn.commit()
        cursor.close()
        return render_template('index.html')
    
#Authenticate staff register
@app.route('/registerAuthStaff', methods=['GET', 'POST'])
def registerAuthStaff():
	#grabs information from the forms
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    airline_name = request.form['airline_name']
    phone_num = request.form['phone_num']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

	#cursor used to send queries
    cursor = conn.cursor()
	#executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
	#stores the results in a variable
    data = cursor.fetchone()
    error = None
    if(data):
		#If the previous query returns data, then account exists
        error = "This account already exists"
        return render_template('register.html', error = error)
    else:
        # insert into airline_staff
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, airline_name, password, first_name, last_name, date_of_birth))
        conn.commit()
        phone_nums = phone_num.split('%2C')
        emails = email.split('%2C')
        # insert all phone numbers into staff_phone
        for num in phone_nums:
            ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
            cursor.execute(ins, (username, phone_num))
            conn.commit()
        # insert all email into staff_email
        for emailAddr in emails:
            ins = 'INSERT INTO staff_email VALUES(%s, %s)'
            cursor.execute(ins, (username, emailAddr))
            conn.commit()
        cursor.close()
        return render_template('index.html')
    
#View public info
@app.route('/viewPublicInfo')
def viewPublicInfo():
    #executes query
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime FROM flight ORDER BY dept_datetime'
    cursor.execute(query)
    #stores all flight status in variable data
    data = cursor.fetchmany(10) 
    cursor.close()
    return render_template('viewPublicInfo.html',schedule=data)

#Search flight
@app.route('/searchFlight', method=['GET', 'POST'])
def viewPublicInfo():
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    dest_city = request.form['dest_city']
    dest_airport = request.form['dest_airport']
    dept_date = request.form['dept_date']
    arrive_date = request.form['arrive_date']
    #executes query
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime FROM flight ORDER BY dept_datetime'
    cursor.execute(query)
    #stores the first 10 flights in variable data
    data = cursor.fetchmany(10) 
    cursor.close()
    #TODO: display data but where? createa another link?





