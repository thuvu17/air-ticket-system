# This file contains customer homepage and all use cases
#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime
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


# STAFF HOME PAGE
@app.route('/homeStaff', methods=['GET', 'POST'])
def homeStaff():
    username = session['username']
    cursor = conn.cursor()
    # GET FIRST NAME FOR WELCOME MESSAGE
    query = 'SELECT first_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    first_name = cursor.fetchone()[first_name]
    # VIEW MY FLIGHTS
    getFlights = 'SELECT F.flight_num, D.city, F.dept_airport, F.dept_datetime, A.city, F.arrive_airport, F.arrive_datetime, F.status FROM flight as F, airport as A, airport as D where F.arrive_airport = A.airport_code and F.dept_airport = D.airport_code and F.dept_datetime and F.airline_name = %s in (SELECT DATEADD(day, 30, SELECT GETDATE())) ORDER BY F.dept_datetime'
    # TODO: how to find the airline_name for the staff
    airline_name = #find airline_name
    cursor.execute(getFlights, (airline_name))
    my_flights_fetch = cursor.fetchall()
    my_flights = []
    for each in my_flights_fetch:
        my_flights.append({"flight_num":each[0], "dept_city":each[1], "dept_airport":each[2], "dept_datetime":each[3], "arrive_city":each[4], "arrive_airport":each[5], "arrive_datetime":each[6]})
    cursor.close()
    #return render_template('homeStaff.html', first_name=first_name)
