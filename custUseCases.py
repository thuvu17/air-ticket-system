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


# CUSTOMER HOMEPAGE
@app.route('/homeCust', methods=['GET'])
def homeCust():
    email = session['email']
    cursor = conn.cursor()
    # get first name for welcome message
    query = 'SELECT first_name FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    first_name = cursor.fetchone()['first_name']
    # get purchased flights that already done
    getDoneFlights = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime \
        FROM flight natural join ticket natural join purchases natural join customer \
            WHERE email = %s and dept_datetime < %s ORDER BY dept_datetime'
    cursor.execute(getDoneFlights, (email, datetime.now()))
    done_flights = cursor.fetchall()
    # get purchased flights that are incoming
    getUpcomingFlights = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime \
        FROM flight natural join ticket natural join purchases natural join customer \
            WHERE email = %s and dept_datetime >= %s ORDER BY dept_datetime'
    cursor.execute(getUpcomingFlights, (email, datetime.now()))
    upcoming_flights = cursor.fetchall()
    cursor.close()
    return render_template('homeCust.html', first_name=first_name, done_flights=done_flights, \
                           upcoming_flights=upcoming_flights)


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






        
