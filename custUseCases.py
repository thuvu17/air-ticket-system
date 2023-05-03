# This file contains customer homepage and all use cases

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
    getUpcomingFlights = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime, ticket_id \
        FROM flight natural join ticket natural join purchases natural join customer \
            WHERE email = %s and dept_datetime >= %s ORDER BY dept_datetime'
    cursor.execute(getUpcomingFlights, (email, datetime.now()))
    upcoming_flights = cursor.fetchall()
    cursor.close()
    return render_template('homeCust.html', first_name=first_name, done_flights=done_flights, \
                           upcoming_flights=upcoming_flights)


# CUSTOMER CANCEL TRIP
@app.route('/custCancelTrip', methods=['GET', 'POST'])
def custCancelTrip():
    cursor = conn.cursor()
    # check if flight is in more than 24 hours
    dept_datetime = request.form['dept_datetime']
    error = None
    # if <= 24 hours, do not allow cancel
    if dept_datetime <= datetime.now() + timedelta(days=1):
        error = "You can only cancel flights that will take place in more than 24 hours!"
        return render_template('custCancelTripConfirm.html', error=error)
    # else, remove purchase of flight
    else:
        ticket_id = request.form['ticket_id']
        # remove from purchase
        popPurchase = 'DELETE FROM purchases WHERE ticket_id = %s'
        cursor.execute(popPurchase, (ticket_id))
        conn.commit()
        # remove from ticket
        popTicket = 'DELETE FROM ticket WHERE ticket_id = %s'
        cursor.execute(popTicket, (ticket_id))
        conn.commit()
        return render_template('custCancelTripConfirm.html', error=error)



# CUSTOMER SEARCH FLIGHTS
search_query = 'SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, arrive_datetime \
    FROM (SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, arrive_datetime \
        FROM flight natural join airport natural join airplane WHERE date(dept_datetime) = "{}" and \
            arrive_airport = airport_code and name = "{}" and city = "{}") sub natural join airport \
                WHERE dept_airport = airport_code and name = "{}" and city = "{}"'

@app.route('/custSearchFlight', methods=['GET', 'POST'])
def custSearchFlight():
    if request.method == 'POST':
        cursor = conn.cursor()
        # get search info
        one_or_round = request.form['one_or_round']
        source_city = request.form['source_city']
        source_airport = request.form['source_airport']
        dest_city = request.form['dest_city']
        dest_airport = request.form['dest_airport']
        dept_date = request.form['dept_date']
        # if one way
        if one_or_round == "one":
            search = search_query.format(dept_date, dest_airport, dest_city, source_airport, source_city)
            cursor.execute(search)
            oneFlights = cursor.fetchall()
            cursor.close()
            return render_template('custOneWayResult.html', oneFlights=oneFlights)
        # if round trip
        else:
            return_date = request.form['return_date']
            searchForward = search_query.format(dept_date, dest_airport, dest_city, source_airport, source_city)
            searchReturn = search_query.format(return_date, source_airport, source_city, dest_airport, dest_city)
            # search forward flights
            cursor.execute(searchForward)
            forwardFlights = cursor.fetchall()
            # search return flights
            cursor.execute(searchReturn)
            returnFlights = cursor.fetchall()
            cursor.close()
            return render_template('custRoundResult.html', forwardFlights=forwardFlights, returnFlights=returnFlights)
    else:
        return render_template('custSearchFlight.html')


# TODO
# CUSTOMER PURCHASE
@app.route('/custPurchase', methods=['POST'])
def custPurchase():
    cursor = conn.cursor()
    # getting all the information for purchase
    if 'custPurchase.html' not in request.referrer:
        # get flight information 
        airline_name = request.form['airline_name']
        flight_num = request.form['flight_num']
        dept_datetime = request.form['dept_datetime']
        query = 'SELECT dept_airport, arrive_airport, arrive_datetime, base_price FROM flight WHERE\
            airline_name = %s and flight_num = %s and dept_datetime = %s'
        cursor.execute(query, (airline_name, flight_num, dept_datetime))
        flightInfo = cursor.fetchone()
        base_price = flightInfo['base_price']
        # get availability
        getSeats = 'SELECT seats FROM airplane natural join flight WHERE airline_name = %s and\
                    flight_num = %s and dept_datetime = %s'
        cursor.execute(getSeats, (airline_name, flight_num, dept_datetime))
        seats = cursor.fetchone()['seats']
        getNumTickets = 'SELECT count(*) as numTickets FROM ticket WHERE airline_name = %s and \
            flight_num = %s and dept_datetime = %s'
        cursor.execute(getNumTickets, (airline_name, flight_num, dept_datetime))
        numTickets = cursor.fetchone()['numTickets']
        availability = seats - numTickets
        cursor.close()
        # calculate final price based on availability
        if availability <= 0.2 * seats:
            additional_price = 0.25 * base_price
        else:
            additional_price = 0
        final_price = base_price + additional_price
        return render_template('custPurchase.html', airline_name=airline_name, flight_num=flight_num, \
                               dept_datetime=dept_datetime, flightInfo=flightInfo, \
                                additional_price=additional_price, final_price=final_price, numTickets=numTickets)
    # process purchase
    else:
        email = session['email']
        final_price = request.form['final_price']
        numTickets = request.form['numTickets']
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
        data = cursor.fetchone()['card_num']
        # if its not already in the system, add
        if not data:
            insPayment = 'INSERT INTO payment_info VALUES (%s, %s, %s, %s)'
            cursor.execute(insPayment, (card_num, card_type, card_name, exp_date))
            conn.commit()
        # INSERT INTO TICKET
        ticket_id = "{}{}".format(email, numTickets + 1)
        insTicket = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(insTicket, (ticket_id, airline_name, flight_num, dept_datetime, \
                                   first_name, last_name, date_of_birth))
        conn.commit()
        # INSERT INTO PURCHASES
        insPurchases = 'INSERT INTO purchases VALUES (%s, %s, %s, %s, %s, NULL, NULL)'
        cursor.execute(insPurchases, (ticket_id, card_num, email, datetime.now(), final_price))
        conn.commit()
        cursor.close()
        return render_template('custPurchaseConfirm.html', airline_name=airline_name, flight_num=flight_num,\
                               flightInfo=flightInfo, dept_datetime=dept_datetime, final_price=final_price)





        
