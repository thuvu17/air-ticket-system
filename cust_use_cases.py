# This file contains customer homepage and all use cases

# Import Flask Library
from flask import Flask, render_template, request, session
from datetime import datetime, timedelta
from setup import app, conn


# CUSTOMER HOMEPAGE
@app.route('/home_cust', methods=['GET'])
def home_cust():
    email = session['email']
    cursor = conn.cursor()
    # get first name for welcome message
    query = 'SELECT first_name FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    first_name = cursor.fetchone()['first_name']
    # get purchased flights that already done
    get_done_flights = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime, ticket_id, \
        first_name, last_name FROM flight natural join ticket natural join purchases \
            WHERE email = %s and dept_datetime < %s ORDER BY dept_datetime'
    cursor.execute(get_done_flights, (email, datetime.now()))
    done_flights = cursor.fetchall()
    # get purchased flights that are incoming
    get_upcoming = 'SELECT airline_name, flight_num, arrive_datetime, dept_datetime, ticket_id, \
        first_name, last_name FROM flight natural join ticket natural join purchases \
            WHERE email = %s and dept_datetime >= %s ORDER BY dept_datetime'
    cursor.execute(get_upcoming, (email, datetime.now()))
    upcoming_flights = cursor.fetchall()
    cursor.close()
    return render_template('home_cust.html', first_name=first_name, done_flights=done_flights, \
                           upcoming_flights=upcoming_flights)


# CUSTOMER CANCEL TRIP
@app.route('/cust_cancel_trip', methods=['GET', 'POST'])
def cust_cancel_trip():
    cursor = conn.cursor()
    # check if flight is in more than 24 hours
    dept_datetime = request.form['dept_datetime']
    error = None
    # if <= 24 hours, do not allow cancel
    if dept_datetime <= datetime.now() + timedelta(days=1):
        error = "You can only cancel flights that will take place in more than 24 hours!"
        return render_template('cust_cancel_trip_confirm.html', error=error)
    # else, remove purchase of flight
    else:
        ticket_id = request.form['ticket_id']
        # remove from purchase
        pop_purchase = 'DELETE FROM purchases WHERE ticket_id = %s'
        cursor.execute(pop_purchase, (ticket_id))
        conn.commit()
        # remove from ticket
        pop_ticket = 'DELETE FROM ticket WHERE ticket_id = %s'
        cursor.execute(pop_ticket, (ticket_id))
        conn.commit()
        return render_template('cust_cancel_trip_confirm.html', error=error)



# CUSTOMER SEARCH FLIGHTS
search_query = 'SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, arrive_datetime \
    FROM (SELECT airline_name, flight_num, dept_airport, arrive_airport, dept_datetime, arrive_datetime \
        FROM flight natural join airport natural join airplane WHERE date(dept_datetime) = "{}" and \
            arrive_airport = airport_code and name = "{}" and city = "{}") sub natural join airport \
                WHERE dept_airport = airport_code and name = "{}" and city = "{}"'

@app.route('/cust_search_flight', methods=['GET', 'POST'])
def cust_search_flight():
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
            one_flights = cursor.fetchall()
            cursor.close()
            return render_template('cust_one_way_result.html', one_flights=one_flights)
        # if round trip
        else:
            return_date = request.form['return_date']
            search_forward = search_query.format(dept_date, dest_airport, dest_city, source_airport, source_city)
            search_return = search_query.format(return_date, source_airport, source_city, dest_airport, dest_city)
            # search forward flights
            cursor.execute(search_forward)
            forward_flights = cursor.fetchall()
            # search return flights
            cursor.execute(search_return)
            return_flights = cursor.fetchall()
            cursor.close()
            return render_template('cust_round_result.html', forward_flights=forward_flights, return_flights=return_flights)
    else:
        return render_template('cust_search_flight.html')


# CUSTOMER PURCHASE
@app.route('/cust_purchase', methods=['POST'])
def cust_purchase():
    email = session['email']
    referrer = request.headers.get('Referer')
    cursor = conn.cursor()
    # get flight info
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    # getting all the information for purchase
    if 'cust_purchase' not in referrer:
        # get flight information 
        query = 'SELECT dept_airport, arrive_airport, arrive_datetime, base_price FROM flight WHERE \
            airline_name = %s and flight_num = %s and dept_datetime = %s'
        cursor.execute(query, (airline_name, flight_num, dept_datetime))
        flight_info = cursor.fetchone()
        base_price = flight_info['base_price']
        # get availability
        get_seats = 'SELECT seats FROM airplane natural join flight WHERE airline_name = %s and\
                    flight_num = %s and dept_datetime = %s'
        cursor.execute(get_seats, (airline_name, flight_num, dept_datetime))
        seats = cursor.fetchone()['seats']
        get_num_tickets = 'SELECT count(*) as num_tickets FROM ticket WHERE airline_name = %s and \
            flight_num = %s and dept_datetime = %s'
        cursor.execute(get_num_tickets, (airline_name, flight_num, dept_datetime))
        num_tickets = cursor.fetchone()['num_tickets']
        availability = seats - num_tickets
        cursor.close()
        # calculate final price based on availability
        if availability <= 0.2 * seats:
            additional_price = 0.25 * base_price
        else:
            additional_price = 0
        final_price = base_price + additional_price
        return render_template('cust_purchase.html', airline_name=airline_name, flight_num=flight_num, \
                               dept_datetime=dept_datetime, flight_info=flight_info, base_price=base_price, \
                                additional_price=additional_price, final_price=final_price, num_tickets=num_tickets)
    # process purchase
    else:
        final_price = float(request.form['final_price'])
        num_tickets = int(request.form['num_tickets'])
        # payment information
        card_num = request.form['card_num']
        card_type = request.form['card_type']
        card_name = request.form['card_name']
        exp_date = request.form['exp_date']
        # passenger information 
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        # CHECK IF CUSTOMER ALREADY PURCHASED THE FLIGHT
        check = 'SELECT * FROM flight natural join ticket natural join purchases \
        WHERE airline_name = %s and flight_num = %s and dept_datetime = %s \
            and email = %s and first_name = %s and last_name = %s'
        cursor.execute(check, (airline_name, flight_num, dept_datetime, email, first_name, last_name))
        data = cursor.fetchone()
        print(data)
        error = None
        if data:
            cursor.close()
            error = "You already booked this ticket!"
            return render_template('cust_purchase_confirm.html', error=error)
        else:
            # INSERT TO PAYMENT_INFO
            check_card_num = 'SELECT card_num FROM payment_info WHERE card_num = %s'
            cursor.execute(check_card_num, (card_num))
            data = cursor.fetchone()
            # if its not already in the system, add
            if not data:
                ins_payment = 'INSERT INTO payment_info VALUES (%s, %s, %s, %s)'
                cursor.execute(ins_payment, (card_num, card_type, card_name, exp_date))
                conn.commit()
            # INSERT INTO TICKET
            ticket_id = "{}{}".format(email[:2], str(num_tickets + 1))
            ins_ticket = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(ins_ticket, (ticket_id, airline_name, flight_num, dept_datetime, \
                                    first_name, last_name, date_of_birth))
            conn.commit()
            # INSERT INTO PURCHASES
            ins_purchases = 'INSERT INTO purchases VALUES (%s, %s, %s, %s, %s, NULL, NULL)'
            cursor.execute(ins_purchases, (ticket_id, card_num, email, datetime.now(), final_price))
            conn.commit()
            cursor.close()
            return render_template('cust_purchase_confirm.html', error=error)
        

# CUSTOMER RATE
@app.route('/cust_rate', methods=['POST'])
def cust_rate():
    email = session['email']
    cursor = conn.cursor()
    referrer = request.headers.get('Referer')
    ticket_id = request.form['ticket_id']
    if 'home_cust' in referrer:
        return render_template('cust_rate.html', ticket_id=ticket_id)
    else:
        # ADD RATING AND COMMENT
        rating = request.form['rating']
        comment = request.form['comment']
        query = 'UPDATE purchases SET rating = %s, comment = %s WHERE email = %s and ticket_id = %s'
        cursor.execute(query, (rating, comment, email, ticket_id))
        conn.commit()
        cursor.close()
        return render_template('cust_rate_confirm.html')



# CUSTOMER TRACK SPENDING
@app.route('/cust_track_spending', methods=['GET', 'POST'])
def cust_track_spending():
    email = session['email']
    cursor = conn.cursor()
    # total amount in past year
    year = datetime.now().year
    today = datetime.now().date().strftime("%Y-%m-%d")
    get_total = 'SELECT sum(calc_price) as total_spending FROM purchases WHERE \
        email = %s and year(date_time) = %s'
    cursor.execute(get_total, (email, year))
    total_spending = cursor.fetchone()['total_spending']
    # month wise amount in past 6 months
    get_month_wise = 'SELECT month(date_time) as month, sum(calc_price) as month_spending \
        FROM purchases WHERE email = %s and datediff(%s, date(date_time)) > %s and \
            datediff(%s, date(date_time)) <= %s GROUP BY month(date_time)'
    cursor.execute(get_month_wise, (email, today, 0, today, 180))
    month_wise = cursor.fetchall()
    if request.method == 'GET':
        search = None
    else:
        # fetch data
        start = request.form['start']
        end = request.form['end']
        search_query = 'SELECT month(date_time) as month, sum(calc_price) as month_spending \
        FROM purchases WHERE email = %s and date(date_time) >= %s and date(date_time) <= %s \
            GROUP BY month(date_time)'
        cursor.execute(search_query, (email, start, end))
        search = cursor.fetchall()
    cursor.close()
    return render_template('cust_track_spending.html', year=year, total_spending=total_spending, \
                           month_wise=month_wise, search=search)


        
