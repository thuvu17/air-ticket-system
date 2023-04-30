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
# ------------------------------------------------------------
# HOMEPAGE WHEN NOT LOGGED IN 
# ---------------------------
# LOGIN
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
	if data:
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('homeStaff'))
	else:
		#returns an error message to the html page
		error = 'Invalid username or password'
		return render_template('loginStaff.html', error=error)


#Authenticates the login for customer
@app.route('/loginAuthCust', methods=['GET', 'POST'])
def loginAuthCust():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	#executes query
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
	cursor.execute(query, (email, password))
	#stores the results in a variable
	data = cursor.fetchone()
	cursor.close()
	error = None
	if data:
		#creates a session for the the user
		session['email'] = email
		return redirect(url_for('homeCust'))
	else:
		#returns an error message to the html page
		error = 'Invalid email or password'
		return render_template('loginCust.html', error=error)
# ------------------------------------------------------------
# REGISTER
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
    if data:
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
    if data:
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
   
# VIEW PUBLIC INFO
@app.route('/viewPublicInfo', method=['GET', 'POST'])
def viewPublicInfo():
    #display first 10 flights
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime FROM flight ORDER BY dept_datetime'
    cursor.execute(query)
    view = cursor.fetchmany(10) 
    #request data from user and display searched flight
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    dest_city = request.form['dest_city']
    dest_airport = request.form['dest_airport']
    dept_date = request.form['dept_date']
    arrive_date = request.form['arrive_date']
    # TODO: query not done
    query = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime FROM flight ORDER BY dept_datetime'	
    cursor.execute(query, (source_city, source_airport, dest_city, dest_airport, dept_date, arrive_date))
    search = cursor.fetchone()
    cursor.close()
    return render_template('viewPublicInfo.html',view=view, search=search)

# ------------------------------------------------------------
# CUSTOMER USE CASES
# Customer homepage
@app.route('/homeCust', method=['GET', 'POST'])
def homeCust():
    email = session['email']
    cursor = conn.cursor()
    # GET FIRST NAME FOR WELCOME MESSAGE
    query = 'SELECT first_name FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    first_name = cursor.fetchone()
    # VIEW MY FLIGHTS
    # TODO: query that displays all upcoming flights of customer
    getFlights = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime FROM flight ORDER BY dept_datetime'
    cursor.execute(getFlights, (email))
    my_flights = cursor.fetchall()
    # SEARCH FLIGHTS
    #request data from user and display searched flight
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    dest_city = request.form['dest_city']
    dest_airport = request.form['dest_airport']
    dept_date = request.form['dept_date']
    arrive_date = request.form['arrive_date']
    # TODO: query include airline, flight num, arr and dept date, base price, availability = seats - count(ticket)
    query = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime, base_price FROM flight ORDER BY dept_datetime'
    cursor.execute(query, (source_city, source_airport, dest_city, dest_airport, dept_date, arrive_date))
    search = cursor.fetchall()
    cursor.close()
    return render_template('homeCust.html', first_name=first_name, my_flights=my_flights, search=search)

@app.route('/purchase', method=['GET'])
def purchase():
    cursor = conn.cursor()
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_daetetime = request.form['dept_datetime']
    # TODO: query to decrement number of availability
    cursor.execute(query)
    cursor.close()

# ------------------------------------------------------------
# STAFF USE CASES
# Staff homepage
@app.route('/homeStaff', method=['GET', 'POST'])
def homeStaff():
    username = session['username']
    cursor = conn.cursor()
    # get first name for welcome message
    query = 'SELECT first_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    first_name = cursor.fetchone()
    # display flights in the next 30 days
    # TODO: query get flight_num, dept and arrival city/airport/datetime, status within 30 days
    getFlights = 'SELECT first_name FROM airline_staff WHERE username = %s'
    cursor.execute(getFlights, (username))
    flights = cursor.fetchall()
    cursor.close()
    return render_template('homeStaff.html', first_name=first_name, flights=flights)

# Staff add airplane
@app.route('/staffAddAirplane', method=['GET'])
def staffAddAirplane():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()
    # get airplane info for adding
    plane_id = request.form['plane_id']
    seats = request.form['seats']
    company = request.form['company']
    manu_date = request.form['manu_date']
	# check if airplane is already in the system
    query = 'SELECT airline_name, plane_id FROM airplane WHERE airline_name = %s, plane_id = %s'
    cursor.execute(query, (airline_name, plane_id))
	#stores the results in a variable
    data = cursor.fetchone()
    error = None
    if data:
		# If the previous query returns data, then airplane exists
        error = "This airplane already exists"
        return render_template('staffAddAirplane.html', error = error)
    else:
        ins = 'INSERT INTO airplane VALUES (%s, %s, %s, %s)'
        cursor.execute(ins, (airline_name, plane_id, seats, company, manu_date))
        conn.commit()
        cursor.close()
        return redirect(url_for('addAirplaneConfirm'))  #  redirect to confirmation page
  

# TODO: add airplane conformation page: see all the airplanes owned by the airline
# Staff change status
@app.route('/addAirplaneConfirm', method=['POST'])
def addAirplaneConfirm():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()
   # get all airplanes of that airline
    getPlanes = 'SELECT plane_id, seats, company, manu_date FROM airplane WHERE airline_name = %s'
    cursor.execute(getPlanes, (airline_name))
    planes = cursor.fetchall()
    cursor.close()
    return render_template('addAirplaneConfirm.html', airline_name=airline_name, planes=planes)

# Staff change status
@app.route('/staffChangeStatus', method=['GET'])
def staffChangeStatus():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()
   # request airplane info for changing status
    newStatus = request.form['newStatus']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    edit = 'UPDATE flight SET status = %s WHERE airline_name = %s and flight_num = %s and dept_datetime = %s'
    cursor.execute(edit, (newStatus, airline_name, flight_num, dept_datetime))
    conn.commit()
    cursor.close()
    return redirect(url_for('homeStaff'))
