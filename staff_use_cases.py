# This file contains staff homepage and all use cases

# Import Flask Library
from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime, timedelta
from setup import app, conn


# HELPER FUNCTION
# get staff info
def get_staff_info(cursor, attribute, username):
    """
    take in the attribute(string) and return value from airline_staff
    with the matching username
    """
    query = "SELECT {} FROM airline_staff WHERE username = %s".format(attribute)
    cursor.execute(query, (username))
    return cursor.fetchone()[attribute]

# get flight info
def get_flight_info(cursor, condition):
    """
    get ALL flights info: flight_num, dept and arrive_city + airport + datetime, status
    with corresponding condition(string)
    """
    where_clause = " and {}".format(condition)
    query = 'SELECT flight_num, dept.city as dept_city, dept.name as dept_airport, dept_datetime, \
        arr.city as arrive_city, arr.name as arrive_airport, arrive_datetime, status \
        FROM airport dept, flight, airport arr WHERE arrive_airport = arr.airport_code \
        and dept_airport = dept.airport_code' + where_clause
    cursor.execute(query)
    return cursor.fetchall()

# get all <attribute> from <relation>
def get_all(cursor, attribute, relation, condition = ''):
    """
    get ALL attribute(string) from a relation(string)
    """
    if condition != '':
        condition = ' WHERE ' + condition
    query = 'SELECT {} FROM {}'.format(attribute, relation) + condition
    print(query)
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
    condition = "airline_name = '{}' and datediff(date(dept_datetime), '{}') > 0 and \
            datediff(date(dept_datetime), '{}') <= 30".format(airline_name, today, today)
    flights = get_flight_info(cursor, condition)
    cursor.close()
    return render_template('home_staff.html', airline_name=airline_name, \
                           first_name=first_name, flights=flights)


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
@app.route('/staff/view_ratings', methods=['POST'])
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
    cursor.close()
    comments = []
    for each in comments_fetch:
        comments.append({'name': each['first_name'] + ' ' + each['last_name'], \
                         'rating': each['rating'], 'comment': each['comment']})
    return render_template('/staff/view_ratings.html', airline_name=airline_name, \
                           flight_num=flight_num, avg_rating=avg_rating, comments=comments)


# STAFF VIEW CUSTOMERS OF A FLIGHT
@app.route('/staff/view_flight_customers', methods=['POST'])
def staff_view_flight_customers():
    """
    display all customers of the flight
    """
    cursor = conn.cursor()
    # get flight info
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    # get list of customers - email, first +  last name
    get_customers = 'SELECT email, first_name, last_name FROM customer natural join \
            (SELECT email FROM purchases natural join ticket WHERE airline_name = %s and \
            flight_num = %s and dept_datetime = %s) sub'
    cursor.execute(get_customers, (airline_name, flight_num, dept_datetime))
    customers = cursor.fetchall()
    cursor.close()
    return render_template('/staff/view_flight_customers.html', airline_name=airline_name, \
                           flight_num=flight_num, customers=customers)



# STAFF VIEW ALL CUSTOMERS
@app.route('/staff/view_customers', methods=['GET'])
def staff_view_customers():
    """
    display most frequent customer of the airline + list of all customers
    """
    cursor = conn.cursor()
    # get airline
    username = session['username']
    airline_name = get_staff_info(cursor, 'airline_name', username)
    # getcustomer's email + first + last name + number of tickets from this airline
    get_customers = 'SELECT email, first_name, last_name, num_tickets \
                    FROM customer NATURAL JOIN ( SELECT email, count(ticket_id) as num_tickets \
                                    FROM purchases NATURAL JOIN ticket \
                                    WHERE airline_name = %s GROUP BY email) sub\
                    ORDER BY num_tickets DESC'
    cursor.execute(get_customers, (airline_name))
    customers = cursor.fetchall()
    cursor.close()
    most_freq = customers[0]
    return render_template('/staff/view_customers.html', airline_name=airline_name, \
                           most_freq=most_freq, customers=customers)



# STAFF VIEW ALL CUSTOMERS' FLIGHTS
@app.route('/staff/view_customer_flights', methods=['POST'])
def staff_view_customer_flights():
    """
    display all flights in this airline that the customer booked
    """
    cursor = conn.cursor()
    # fetch customer email
    email = request.form['email']
    # get airline
    username = session['username']
    airline_name = get_staff_info(cursor, 'airline_name', username)
    # get passenger's first + last name + flight info
    select_clause = 'SELECT flight.flight_num, dept.city as dept_city, dept.name as dept_airport, \
        flight.dept_datetime, arr.city as arrive_city, arr.name as arrive_airport, \
        arrive_datetime, status, first_name, last_name '
    
    from_clause = 'FROM airport dept, flight, airport arr, ticket, purchases '

    where_clause = 'WHERE arrive_airport = arr.airport_code and dept_airport = dept.airport_code \
        and flight.airline_name = ticket.airline_name and flight.flight_num = ticket.flight_num and \
        flight.dept_datetime = ticket.dept_datetime and ticket.ticket_id = purchases.ticket_id and \
        email = %s and flight.airline_name = %s'
    
    get_flights = select_clause + from_clause + where_clause
    cursor.execute(get_flights, (email, airline_name))
    flights = cursor.fetchall()
    cursor.close()
    return render_template('/staff/view_customer_flights.html', airline_name=airline_name, \
                           email=email, flights=flights)



# STAFF CHANGE FLIGHT STATUS
@app.route('/staff/change_status', methods=['POST'])
def staff_change_status():
    """
    change flight status
    """
    cursor = conn.cursor()
    # fetch flight info
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    old_status = request.form['old_status']
    new_status = request.form['new_status']
    # update new status and redirect to confirmation page
    if old_status != new_status:
        change_status = 'UPDATE flight SET status = %s WHERE airline_name = %s and \
            flight_num = %s and dept_datetime = %s'
        cursor.execute(change_status, (new_status, airline_name, flight_num, dept_datetime))
        cursor.close()
        return render_template('/staff/change_status_confirm.html')
    else:
        cursor.close()
        return redirect(url_for('staff_view_flights')) 
    


# STAFF CREATE NEW FLIGHTS
@app.route('/staff/create_flight', methods=['GET','POST'])
def staff_create_flight():
    """
    take in flight info via forms and create new flight if it hasn't already existed
    """
    # get airline
    cursor = conn.cursor()
    username = session['username']
    airline_name = get_staff_info(cursor, 'airline_name', username)
    # get all airports and airlines
    airports = get_all(cursor, 'airport_code', 'airport')
    airlines = get_all(cursor, 'airline_name', 'airline')

    # IF POST REQUEST - INSERTING NEW FLIGHT
    if request.method == 'POST':
        # fetch all flight info
        flight_num = request.form['flight_num']
        dept_datetime = request.form['dept_datetime']
        plane_airline = request.form['plane_airline']
        plane_id = request.form['plane_id']
        arrive_datetime = request.form['arrive_datetime']
        arrive_airport = request.form['arrive_airport']
        dept_airport = request.form['dept_airport']
        status = request.form['status']
        base_price = request.form['base_price']

        # CHECK IF DATETIME IS VALID
        if arrive_datetime < dept_datetime:
            error = 'Arrival must be after departure. Please try again'
            cursor.close()
            return render_template('/staff/create_flight.html', error=error, \
                    airline_name=airline_name, airports=airports, airlines=airlines)
        
        # CHECK IF AIRPORT IS VALID
        if arrive_airport == dept_airport:
            error = 'Arrive airport must be different from departure airport. Please try again'
            cursor.close()
            return render_template('/staff/create_flight.html', error=error, \
                    airline_name=airline_name, airports=airports, airlines=airlines)

        # CHECK IF STAFF INSERTED A VALID AIRPLANE
        check_plane = 'SELECT * FROM airplane WHERE airline_name = %s and plane_id = %s'
        cursor.execute(check_plane, (plane_airline, plane_id))
        plane = cursor.fetchone()
        if not plane:
            error = 'Airplane is not in the system. Please try again.'
            cursor.close()
            return render_template('/staff/create_flight.html', error=error, \
                    airline_name=airline_name, airports=airports, airlines=airlines)  
        
        # CHECK IF FLIGHT ALREADY EXISTED
        condition = "airline_name = '{}' and flight_num = '{}' and \
            dept_datetime = '{}'".format(airline_name, flight_num, dept_datetime)
        flight = get_flight_info(cursor, condition)
        # if flight is not in the system, create flight
        if not flight:
            create_flight = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(create_flight, (airline_name, flight_num, dept_datetime, plane_airline, \
                            plane_id, arrive_datetime, arrive_airport, dept_airport, status, base_price))
            conn.commit()
            # get flights in the next 30 days
            today = datetime.now().date().strftime("%Y-%m-%d")
            condition_30_days = "airline_name = '{}' and datediff(date(dept_datetime), '{}') > 0 and \
                        datediff(date(dept_datetime), '{}') <= 30".format(airline_name, today, today)
            flights = get_flight_info(cursor, condition_30_days)
            cursor.close()
            return render_template('/staff/create_flight_confirm.html', airline_name=airline_name, \
                    flight_num=flight_num, dept_datetime=dept_datetime, plane_id=plane_id, \
                    arrive_datetime=arrive_datetime, dept_airport=dept_airport, \
                    arrive_airport=arrive_airport, status=status, base_price=base_price, flights=flights)
        # if flight is already in the system, give error
        else:
            cursor.close()
            error = "Flight is already in the system"
            return render_template('/staff/create_flight.html', error=error)
    # IF GET REQUEST - LOADING THE PAGE
    else:
        cursor.close()
        return render_template('/staff/create_flight.html', airline_name=airline_name, \
                               airports=airports, airlines=airlines)
    


# STAFF ADD AIRPLANE
@app.route('/staff/add_airplane', methods=['GET','POST'])
def staff_add_airplane():
    """
    take in airplane info via forms and add new airplanae if it hasn't already existed
    """
    # get airline
    cursor = conn.cursor()
    username = session['username']
    airline_name = get_staff_info(cursor, 'airline_name', username)
    if request.method == 'POST':
        # get airplane info from form
        plane_id = request.form['plane_id']
        seats = request.form['seats']
        company = request.form['company']
        manu_date = request.form['manu_date']
        # CHECK IF AIRPLANE ALREADY IN THE SYSTEM
        check = 'SELECT * FROM airplane WHERE airline_name = %s and plane_id = %s'
        cursor.execute(check, (airline_name, plane_id))
        plane = cursor.fetchone()
        if not plane:
            add_plane = 'INSERT INTO airplane VALUES(%s, %s, %s, %s, %s)'
            cursor.execute(add_plane, (airline_name, plane_id, seats, company, manu_date))
            conn.commit()
            # get all airplanes of this airline
            condition = "airline_name = '{}'".format(airline_name)
            planes = get_all(cursor, 'plane_id, seats, company, manu_date', 'airplane', condition)
            cursor.close()
            return render_template('/staff/add_airplane_confirm.html', \
                                   airline_name=airline_name, planes=planes)
        else:
            error = 'Airplane already existed!'
            cursor.close()
            return render_template('/staff/add_airplane.html', airline_name=airline_name, error=error)
    else:
        cursor.close()
        return render_template('/staff/add_airplane.html', airline_name=airline_name)
    

# STAFF ADD AIRPORT
@app.route('/staff/add_airport', methods=['GET','POST'])
def staff_add_airport():
    """
    take in airport info via forms and add new airport if it hasn't already existed
    """
    # get airline
    if request.method == 'POST':
        cursor = conn.cursor()
        # get airport info from form
        airport_code = request.form['airport_code']
        name = request.form['name']
        city = request.form['city']
        country = request.form['country']
        type = request.form['type']
        # CHECK IF AIRPORT ALREADY IN THE SYSTEM
        check = 'SELECT * FROM airport WHERE airport_code = %s'
        cursor.execute(check, (airport_code))
        airport = cursor.fetchone()
        if not airport:
            add_airport = 'INSERT INTO airport VALUES(%s, %s, %s, %s, %s)'
            cursor.execute(add_airport, (airport_code, name, city, country, type))
            conn.commit()
            cursor.close()
            return render_template('/staff/add_airport_confirm.html')
        else:
            cursor.close()
            error = 'Airport is already in the system!'
            return render_template('/staff/add_airport.html', error=error)
    else:
        return render_template('/staff/add_airport.html')
        