# This file contains staff homepage and all use cases

#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime, timedelta
import pymysql.cursors

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


# STAFF USE CASES
# Staff homepage
@app.route('/homeStaff')
def homeStaff():
    username = session['username']
    cursor = conn.cursor()
    # get first name for welcome message
    query = 'SELECT first_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    first_name = cursor.fetchone()[0]
    # get airline name
    query1 = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query1, (username))
    airline_name = cursor.fetchone()[0]
    # display flights in the next 30 days
    # TODO: query get flight_num, dept and arrival city/airport/datetime, status within 30 days
    getFlights = 'SELECT flight_num, dept_city, dept_airport, dept_datetime, arrive_city,\
         arrive_airport, arrive_datetime FROM flight natural join airport WHERE airline_name = %s'
    cursor.execute(getFlights, (airline_name))
    flights_fetch = cursor.fetchall()
    flights = []
    for each in flights_fetch:
        flights.append({"flight_num":each[0], "dept_city":each[1], "dept_airport":each[2],\
                        "dept_datetime":each[3], "arrive_city":each[4], "arrive_airport":each[5],\
                            "arrive_datetime":each[6]})
    cursor.close()
    return render_template('homeStaff.html', first_name=first_name, flights=flights)

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
