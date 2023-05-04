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


# STAFF USE CASES
# STAFF HOMEPAGE
@app.route('/home_staff', methods=['POST', 'GET'])
def home_staff():
    username = session['username']
    cursor = conn.cursor()
    # get staff first name and airline name
    first_name = get_staff_info(cursor, 'first_name', username)
    airline_name = get_staff_info(cursor, 'airline_name', username)
    # display flights in the next 30 days
    # TODO: query get flight_num, dept and arrival city/airport/datetime, status within 30 days

    get_flights = 'SELECT flight_num, dept.city as dept_city, dept.name as dept_airport, dept_datetime, \
        arr.city as arrive_city, arr.name as arrive_airport, arrive_datetime \
            FROM airport dept, flight, airport arr WHERE arrive_airport = arr.airport_code \
                and dept_airport = dept.airport_code and airline_name = %s'
    cursor.execute(get_flights, (airline_name))
    flights = cursor.fetchall()
    cursor.close()
    return render_template('home_staff.html', first_name=first_name, flights=flights)


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
