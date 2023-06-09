# This file contains customer homepage and all use cases

# Import Flask Library
from flask import Flask, render_template, request, session
from datetime import datetime, timedelta
from setup import app, conn
from decimal import Decimal
from staff_use_cases import get_flight_info


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
@app.route('/cust/cancel_trip', methods=['POST'])
def cust_cancel_trip():
    cursor = conn.cursor()
    # check if flight is in more than 24 hours
    dept_datetime = datetime.strptime(request.form['dept_datetime'], '%Y-%m-%d %H:%M:%S')
    error = None
    # if <= 24 hours, do not allow cancel
    if dept_datetime <= datetime.now() + timedelta(days=1):
        error = "You can only cancel flights that will take place in more than 24 hours!"
        return render_template('cust/cancel_trip_confirm.html', error=error)
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
        return render_template('cust/cancel_trip_confirm.html', error=error)



# CUSTOMER SEARCH FLIGHTS
@app.route('/cust/search_flight', methods=['GET', 'POST'])
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
        # condition for query
        condition = "dept.city = '{}' and dept.name = '{}' and \
                arr.city = '{}' and arr.name = '{}' and date(dept_datetime) = '{}'"
        # if one way
        if one_or_round == "one":
            one_condition = condition.format(source_city, source_airport, dest_city, dest_airport, dept_date)
            one_flights = get_flight_info(cursor, one_condition)
            cursor.close()
            return render_template('/cust/one_way_result.html', one_flights=one_flights)
        # if round trip
        else:
            return_date = request.form['return_date']
            forward_condition = condition.format(source_city, source_airport, dest_city, dest_airport, dept_date)
            return_condition = condition.format(dest_city, dest_airport, source_city, source_airport, return_date)
            forward_flights = get_flight_info(cursor, forward_condition)
            return_flights = get_flight_info(cursor, return_condition)
            cursor.close()
            return render_template('/cust/round_result.html', forward_flights=forward_flights, return_flights=return_flights)
    else:
        return render_template('/cust/search_flight.html')


# CUSTOMER PURCHASE
@app.route('/cust/purchase', methods=['POST'])
def cust_purchase():
    email = session['email']
    referrer = request.headers.get('Referer')
    cursor = conn.cursor()
    # get flight info
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_datetime = request.form['dept_datetime']
    print(airline_name, flight_num, dept_datetime)
    # getting all the information for purchase
    if '/cust/purchase' not in referrer:
        # get flight information 
        query = 'SELECT dept_airport, arrive_airport, arrive_datetime, base_price FROM flight WHERE \
            airline_name = %s and flight_num = %s and dept_datetime = %s'
        cursor.execute(query, (airline_name, flight_num, dept_datetime))
        flight_info = cursor.fetchone()
        base_price = flight_info['base_price']
        # get availability
        get_seats = 'SELECT seats FROM airplane, flight WHERE flight.airline_name = %s and\
                    flight_num = %s and dept_datetime = %s and airplane.airline_name = flight.plane_airline \
                    and airplane.plane_id = flight.plane_id'
        cursor.execute(get_seats, (airline_name, flight_num, dept_datetime))
        seats = cursor.fetchone()['seats']
        get_num_tickets = 'SELECT count(*) as num_tickets FROM ticket WHERE airline_name = %s and \
            flight_num = %s and dept_datetime = %s'
        cursor.execute(get_num_tickets, (airline_name, flight_num, dept_datetime))
        num_tickets = cursor.fetchone()['num_tickets']
        availability = seats - num_tickets
        cursor.close()
        # if no more seats
        if availability == 0:
            error = "Sorry, there are no more seats on this flight!"
            return render_template('/cust/purchase_confirm.html', error=error)
        # calculate final price based on availability
        if availability <= 0.2 * seats:
            additional_price = Decimal(0.25) * base_price
        else:
            additional_price = 0
        final_price = base_price + additional_price
        return render_template('/cust/purchase.html', airline_name=airline_name, flight_num=flight_num, \
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
            return render_template('/cust/purchase_confirm.html', error=error)
        else:
            now = datetime.now()
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
            # generate ticket_id = time of purchase + order of purchase
            ticket_id = "{}#{}".format(now.strftime('%H:%M:%S'), str(num_tickets + 1))
            ins_ticket = 'INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(ins_ticket, (ticket_id, airline_name, flight_num, dept_datetime, \
                            first_name, last_name, date_of_birth))
            conn.commit()
            # INSERT INTO PURCHASES
            ins_purchases = 'INSERT INTO purchases VALUES (%s, %s, %s, %s, %s, NULL, NULL)'
            cursor.execute(ins_purchases, (ticket_id, card_num, email, now, final_price))
            conn.commit()
            cursor.close()
            return render_template('/cust/purchase_confirm.html', error=error)
        

# CUSTOMER RATE
@app.route('/cust/rate', methods=['POST'])
def cust_rate():
    email = session['email']
    cursor = conn.cursor()
    referrer = request.headers.get('Referer')
    ticket_id = request.form['ticket_id']
    if 'home_cust' in referrer:
        return render_template('/cust/rate.html', ticket_id=ticket_id)
    else:
        # ADD RATING AND COMMENT
        rating = request.form['rating']
        comment = request.form['comment']
        query = 'UPDATE purchases SET rating = %s, comment = %s WHERE email = %s and ticket_id = %s'
        cursor.execute(query, (rating, comment, email, ticket_id))
        conn.commit()
        cursor.close()
        return render_template('/cust/rate_confirm.html')



# CUSTOMER TRACK SPENDING
@app.route('/cust/track_spending', methods=['GET', 'POST'])
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
    # get month-wise report: spending in the last 6 months within the year
    this_month = datetime.now().month
    this_year = datetime.now().year
    get_month_wise = 'SELECT month(date_time) as month, sum(calc_price) as month_spending \
                    FROM purchases WHERE email = %s and %s > date_time \
                    and datediff(%s, date(date_time)) <= %s GROUP BY month(date_time)'
    cursor.execute(get_month_wise, (email, today, today, 180))
    month_wise = cursor.fetchall()
    if this_month >= 6:
        months = [i for i in range(1, 7)]
    else:
        months = [i for i in range(1, this_month + 1)]
    month_wise_spending = [0 for i in range(len(months))]
    for each in month_wise:
        month_wise_spending[each['month'] - months[0]] = each['month_spending']
    if request.method == 'GET':
        search = None
    # CUSTOMER VIEW SPENDING IN A SPECIFIED RANGE
    else:
        # fetch data
        start = request.form['start']
        end = request.form['end']
        search_query = 'SELECT month(date_time) as month, sum(calc_price) as month_spending \
                        FROM purchases WHERE email = %s and date(date_time) >= %s \
                        and date(date_time) <= %s GROUP BY month(date_time)'
        cursor.execute(search_query, (email, start, end))
        search = cursor.fetchall()
    cursor.close()
    return render_template('/cust/track_spending.html', year=year, total_spending=total_spending, \
                           month_wise_spending=month_wise_spending, months=months, search=search)


        
