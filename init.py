#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime
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

#Define a route to goodbye function
@app.route('/goodbye')
def goodbye():
	return redirect('/')

# LOGIN
@app.route('/loginStaff')
def loginStaff():
    return render_template('loginStaff.html')

@app.route('/loginCust')
def loginCust():
    return render_template('loginCust.html')

# LOGOUT
@app.route('/custLogout')
def custLogout():
	session.pop('email')
	return redirect('/goodbye')

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
        return render_template('register.html', error=error)
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
        return render_template('register.html', error=error)
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

# TODO: search round trip or one way
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
    search_fetch = cursor.fetchone()
    search = {"airline_name":search_fetch[0], "flight_num":search_fetch[1], "arrive_datetime":search_fetch[2], \
              "dept_datetime":search_fetch[3]}
    cursor.close()
    return render_template('viewPublicInfo.html',view=view, search=search)

# ------------------------------------------------------------
# CUSTOMER USE CASES
# CUSTOMER HOME PAGE
@app.route('/homeCust', methods=['GET', 'POST'])
def homeCust():
    email = session['email']
    cursor = conn.cursor()
    # GET FIRST NAME FOR WELCOME MESSAGE
    query = 'SELECT first_name FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    first_name = cursor.fetchone()[0]
    # VIEW MY FLIGHTS
    # TODO: query that displays all upcoming flights of customer
    getFlights = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime FROM flight ORDER BY dept_datetime'
    cursor.execute(getFlights, (email))
    my_flights_fetch = cursor.fetchall()
    my_flights = []
    for each in my_flights_fetch:
        my_flights.append({"airline_name":each[0], "flight_num":each[1], "arrive_datetime":each[2], "dept_datetime":each[3]})
    cursor.close()
    return render_template('homeCust.html', first_name=first_name, my_flights=my_flights)


# CUSTOMER SEARCH FLIGHTS
@app.route('/custSearchFlights', method=['GET', 'POST'])
def custSearchFlights():
    cursor = conn.cursor()
    # search flights
    one_or_round = request.form['one_or_round']
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    dest_city = request.form['dest_city']
    dest_airport = request.form['dest_airport']
    dept_date = request.form['dept_date']
    # if one way
    if one_or_round == "one":
        arrive_date = request.form['arrive_date']
        search = 'SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, \
            arrive_datetime, ??? as availability'  # TODO
        cursor.execute(search, (source_city, source_airport, dest_city, dest_airport, dept_date, arrive_date))
        oneFlights_fetch = cursor.fetchall()
        oneFlights = []
        for each in oneFlights_fetch:
            oneFlights.append({"airline_name":each[0], "flight_num":each[1], "dept_airport":each[2],\
                               "arrive_airport":each[3], "dept_datetime":each[4], "arrive_datetime":each[5], "availability":each[6]})
    # if round trip
    else:
        return_date = request.form['return_date']
        searchForward = 'SELECT *'    # TODO
        searchReturn = 'SELECT *'    # TODO
        # search forward flights
        cursor.execute(searchForward, (source_city, source_airport, dest_city, dest_airport, dept_date, return_date))
        forwardFlights_fetch = cursor.fetchall()
        forwardFlights = []
        for each in forwardFlights_fetch:
            forwardFlights.append({"airline_name":each[0], "flight_num":each[1], "dept_airport":each[2],\
                               "arrive_airport":each[3], "dept_datetime":each[4], "arrive_datetime":each[5], "availability":each[6]})
        # search return flights
        cursor.execute(searchReturn, (source_city, source_airport, dest_city, dest_airport, dept_date, return_date))
        returnFlights_fetch = cursor.fetchall()
        returnFlights = []
        for each in returnFlights_fetch:
            returnFlights.append({"airline_name":each[0], "flight_num":each[1], "dept_airport":each[2],\
                               "arrive_airport":each[3], "dept_datetime":each[4], "arrive_datetime":each[5], "availability":each[6]})
    cursor.close()
    return render_template('custSearchFlights.html', oneFlights=oneFlights, forwardFlights=forwardFlights, returnFlights=returnFlights)

# CUSTOMER PURCHASE
# TODO
@app.route('/custPurchase', methods=['GET', 'POST'])
def custPurchase():
    cursor = conn.cursor()
    email = session['email']
    # flight information 
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    query = 'SELECT dept_airport, arrive_airport, arrive_datetime, base_price FROM flight WHERE\
        airline_name = %s and flight_num = %s and dept_datetime = %s'
    cursor.execute(query, (airline_name, flight_num, dept_datetime))
    flightInfo_fetch = cursor.fetchone()
    flightInfo = {"dept_airport":flightInfo_fetch[0], "arrive_airport":flightInfo_fetch[1], "arrive_datetime":flightInfo_fetch[2],\
                  "base_price":flightInfo_fetch[3]}
    base_price = flightInfo['base_price']
    # get availability
    getSeats = 'SELECT seats FROM airplane natural join flight WHERE airline_name = %s and\
                flight_num = %s and dept_datetime = %s'
    cursor.execute(getSeats, (airline_name, flight_num, dept_datetime))
    seats = cursor.fetchone()[0]
    # TODO: get availability
    getNumTickets = 'SELECT count(*) FROM ticket WHERE airline_name = %s and flight_num = %s \
                    and dept_datetime = %s'
    cursor.execute(getNumTickets, (airline_name, flight_num, dept_datetime))
    numTickets = cursor.fetchone()[0]
    availability = seats - numTickets
    cursor.close()
    # calculate final price based on availability
    if availability <= 0.2:
        additional_price = 0.25 * base_price
    else:
        additional_price = 0
    final_price = base_price + additional_price
    if request.method == 'GET':
        return render_template('custPurchase.html', airline_name=airline_name, flight_num=flight_num, dept_datetime=dept_datetime, \
                               flightInfo=flightInfo, additional_price=additional_price, final_price=final_price)
    else:
        # payment information
        card_num = request.form['card_num']
        card_type = request.form['card_type']
        card_name = request.form['card_name']
        exp_date = request.form['exp_date']
        # passenger information 
        first_name = request.form['first_name']
        last_name = request.form['last_nam']
        date_of_birth = request.form['date_of_birth']
        # INSERT TO PAYMENT_INFO
        checkCardNum = 'SELECT card_num FROM payment_info WHERE card_num = %s'
        cursor.execute(checkCardNum, (card_num))
        data = cursor.fetchone()
        # if its not already in the system, add
        if not data:
            insPayment = 'INSERT INTO payment_info VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(insPayment, (card_num, card_type, card_name, exp_date, final_price))
            conn.commit()
        # INSERT INTO TICKET
        ticket_id = numTickets + 1
        insTicket = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(insTicket, (ticket_id, airline_name, flight_num, dept_datetime, first_name, last_name, date_of_birth))
        conn.commit()
        # INSERT INTO PURCHASES
        date = datetime.now().date()
        time = datetime.now().time()
        insPurchases = 'INSERT INTO purchases VALUES (%s, %s, %s, %s, %s, NULL, NULL)'
        cursor.execute(insPurchases, (ticket_id, card_num, email, date, time))
        conn.commit()
        return render_template('custPurchaseConfirm.html', airline_name=airline_name, flight_num=flight_num,\
                               flightInfo=flightInfo, dept_datetime=dept_datetime, final_price=final_price)


# CUSTOMER CANCEL TRIP
# TODO
@app.route('/custCancelTrip', methods=['GET', 'POST'])
def custCancelTrip():
    cursor = conn.cursor()
    email = session['email']
    # TODO: query to find customer purchased flights
    query = 'SELECT airline_name, flight_num, dept_datetime, arrive_datetime, dept_airport, arrive_airport, ticket_id\
        FROM flight WHERE airline_name = %s and flight_num = %s and dept_datetime = %s'
    cursor.execute(query, (email))
    my_flights = cursor.fetchall()
    if request.method == 'GET':
        cursor.close()
        return render_template('custCancelTrip.html', my_flights=my_flights)
    else:
        ticket_id = request.form['ticket_id']
        # remove from purchase
        popPurchase = 'DELETE FROM purchase WHERE ticket_id = %s'
        cursor.execute(popPurchase, (ticket_id))
        conn.commit()
        # remove from ticket
        popTicket = 'DELETE FROM ticket WHERE ticket_id = %s'
        cursor.execute(popTicket, (ticket_id))
        conn.commit()






        
