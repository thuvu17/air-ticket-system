# This file contains staff homepage and all use cases

# Import Flask Library
from flask import Flask, render_template, request, session
from datetime import datetime, timedelta
from setup import app, conn


# HELPER FUNCTION
def get_staff_info(cursor, attribute, username):
    """
    take in the attribute(string) and return value from airline_staff
    with the matching username
    """
    query = "SELECT {} FROM airline_staff WHERE username = %s".format(attribute)
    cursor.execute(query, (username))
    return cursor.fetchone()[attribute]


def get_flight_info(cursor, condition):
    """
    get flight info including: flight_num, dept and arrive_city + airport + datetime, status
    with corresponding condition(string)
    """
    where_clause = " and {}".format(condition)
    query = 'SELECT flight_num, dept.city as dept_city, dept.name as dept_airport, dept_datetime, \
        arr.city as arrive_city, arr.name as arrive_airport, arrive_datetime, status \
            FROM airport dept, flight, airport arr WHERE arrive_airport = arr.airport_code \
                and dept_airport = dept.airport_code' + where_clause
    cursor.execute(query)
    return cursor.fetchall()


# STAFF USE CASES
# STAFF HOMEPAGE
@app.route('/home_staff', methods=['POST', 'GET'])
def home_staff():
    username = session['username']
    cursor = conn.cursor()
    # get staff first name and airline name
    first_name = get_staff_info(cursor, 'first_name', username)
    airline_name = get_staff_info(cursor, 'airline_name', username)
    today = datetime.now().date().strftime("%Y-%m-%d")
    # display flights in the next 30 days
    condition = "airline_name = '{}' and datediff('{}', date(dept_datetime)) < 0 and \
        datediff('{}', date(dept_datetime)) >= 30".format(airline_name, today, today)
    flights = get_flight_info(cursor, condition)
    cursor.close()
    return render_template('home_staff.html', airline_name=airline_name, \
                           first_name=first_name, flights=flights)


	
	
	
#Session Management
#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('homeStaff'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('registerStaff.html', error = error)
	else:
		ins = 'INSERT INTO airline_staff VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('homeStaff.html')



# STAFF VIEW FLIGHTS
@app.route('/staff_view_flights', methods=['POST', 'GET'])
def staff_view_flights():
    """
    default: display all flights by that airline
    has an option for staff to search by range
    flight info = default + average rating + /link to view all customers + comments
    """
    username = session['username']
    cursor = conn.cursor()
    # get all flights run by this airline
    airline_name = get_staff_info(cursor, 'airline_name', username)
    condition = "airline_name = '{}'".format(airline_name)
    all_flights = get_flight_info(cursor, condition)
    # display flights in the next 30 days
    condition = "airline_name = '{}'".format(airline_name)
    if request.method == 'GET':
        cursor.close()
        return render_template('staff_view_flights.html', airline_name=airline_name, \
                           all_flights=all_flights, request='GET')
    # display flights within specified range
    else:
        start = request.form['start']
        end = request.form['end']
        search_condition = "airline_name = '{}' and date(dept_datetime) >= '{}' \
            and date(dept_datetime) <= '{}'".format(airline_name, start, end)
        search = get_flight_info(cursor, search_condition)
        cursor.close()
        return render_template('staff_view_flights.html', airline_name=airline_name, \
                           all_flights=all_flights, search=search, request='POST')
    

# STAFF VIEW RATINGS
@app.route('/staff_view_ratings', methods=['POST'])
def staff_view_ratings():
    """
    default: display average rating and all comments
    """
    cursor = conn.cursor()
    # get flight info
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    # get avg rating
    get_avg_rating = 'SELECT avg(rating) as avg_rating FROM purchases natural join ticket \
        WHERE airline_name = %s and flight_num = %s and dept_datetime = %s'
    cursor.execute(get_avg_rating, (airline_name, flight_num, dept_datetime))
    avg_rating = cursor.fetchone()['avg_rating']
    # get list of all comments and customer name
    get_comments = 'SELECT first_name, last_name, rating, comment \
        FROM purchases natural join ticket WHERE airline_name = %s and flight_num = %s \
            and dept_datetime = %s and comment is not NULL'
    cursor.execute(get_comments, (airline_name, flight_num, dept_datetime))
    comments_fetch = cursor.fetchall()
    comments = []
    for each in comments_fetch:
        comments.append({'name': each['first_name'] + ' ' + each['last_name'], \
                         'rating': each['rating'], 'comment': each['comment']})
    return render_template('staff_view_ratings.html', airline_name=airline_name, \
                           flight_num=flight_num, avg_rating=avg_rating, comments=comments)


# Staff add airplane
@app.route('/staffAddAirplane', methods=['GET', 'POST'])
def staffAddAirplane():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()[0]
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
        ins = 'INSERT INTO airplane VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(ins, (airline_name, plane_id, seats, company, manu_date))
        conn.commit()
        cursor.close()
        return redirect(url_for('addAirplaneConfirm'))  #  redirect to confirmation page
  

# Confirmation page for addAirplane
@app.route('/addAirplaneConfirm', method=['POST'])
def addAirplaneConfirm():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()[0]
   # get all airplanes of that airline
    getPlanes = 'SELECT plane_id, seats, company, manu_date FROM airplane WHERE airline_name = %s'
    cursor.execute(getPlanes, (airline_name))
    planes_fetch = cursor.fetchall()
    planes = []
    for each in planes_fetch:
        planes.append({"plane_id":each[0], "seats":each[1], "company":each[2], "manu_date":each[3]})
    cursor.close()
    return render_template('addAirplaneConfirm.html', airline_name=airline_name, planes=planes)


# Staff change status
@app.route('/staffChangeStatus', methods=['GET', 'POST'])
def staffChangeStatus():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()[0]
   # request airplane info for changing status
    newStatus = request.form['newStatus']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    edit = 'UPDATE flight SET status = %s WHERE airline_name = %s and flight_num = %s and dept_datetime = %s'
    cursor.execute(edit, (newStatus, airline_name, flight_num, dept_datetime))
    conn.commit()
    cursor.close()
    return redirect(url_for('homeStaff'))


# Staff add airport
@app.route('/staffAddAirport', methods=['GET', 'POST'])
def staffAddAirport():
    username = session['username']
    cursor = conn.cursor()
    # get airline name
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()[0]
    if request.method == "POST":
        # get airport info for adding
        airport_code = request.form['airport_code']
        name = request.form['name']
        city = request.form['city']
        country = request.form['county']
        type = request.form['type']
        # check if airport is already in the system
        check = 'SELECT airport_code FROM airport WHERE airport_code = %s'
        cursor.execute(check, (airport_code))
        #stores the results in a variable
        data = cursor.fetchone()
        error = None
        if data:
            # If the previous query returns data, then airport exists
            error = "This airport already exists"
            return render_template('staffAddAirport.html', error = error)
        else:
            ins = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(ins, (airport_code, name, city, country, type))
            conn.commit()
            cursor.close()
            return redirect(url_for('addAirportConfirm'))  #  redirect to confirmation page
    else:
         return render_template('staffAddAirport.html', airline_name = airline_name)
