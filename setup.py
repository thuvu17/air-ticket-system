from flask import Flask
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

# Secret key
app.secret_key = 'this is the secret key'