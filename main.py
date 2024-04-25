# app.py

from flask import Flask, render_template, request, jsonify,session
import mysql.connector
import datetime
import pytz
import threading  # Import threading module
import time


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key


# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    database="chatnow",
    charset='utf8mb4'
)
cursor = db.cursor()

# Function to keep the connection alive
def keep_connection_alive():
    while True:
        db.ping(reconnect=True)
        time.sleep(300)  # Ping the database server every 5 minutes

# Your existing routes and code...

# Route to handle sending typing status
@app.route('/typing_status', methods=['POST'])
def typing_status():
    username = request.form['username']
    room_name = request.form['room_name']
    typing_status = request.form['typing_status']  # 'typing' or 'not typing'

    # Broadcast typing status to other users in the same room
    cursor.execute("UPDATE chats SET typing_status = %s WHERE username = %s AND room_name = %s", (typing_status, username, room_name))
    db.commit()

    return jsonify({'status': 'OK'})

# Start the keep_connection_alive thread
connection_thread = threading.Thread(target=keep_connection_alive)
connection_thread.daemon = True
connection_thread.start()


print('database connection astoblished')

app.config['JSON_AS_ASCII'] = False

try:
    print('started creating table')
    # Create table if not exists


    cursor.execute("CREATE TABLE IF NOT EXISTS myroom_logs (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255),login_time VARCHAR(255),room_name VARCHAR(255))")
    cursor.execute("CREATE TABLE IF NOT EXISTS myroom_deletion_log (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), deletion_time VARCHAR(100))")
    cursor.execute("CREATE TABLE IF NOT EXISTS myroom_chats (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), msg TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci, msg_time VARCHAR(100), msg_date VARCHAR(100))")
    cursor.execute("CREATE TABLE IF NOT EXISTS registers (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255),login_time VARCHAR(255))")
    cursor.execute("CREATE TABLE IF NOT EXISTS deletion_log (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), deletion_time VARCHAR(100))")
    cursor.execute("CREATE TABLE IF NOT EXISTS chats (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), msg TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci, msg_time VARCHAR(100), msg_date VARCHAR(100))")
    print('table created sucessfully')
except:
    print('table exists')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form['username']
    if username=='':
        return render_template('index.html',error='USE A NAME TO CHAT')
    elif username=='myroom':
        return render_template('myroom_index.html')
    else:
        # Get the current UTC time
        utc_now = datetime.datetime.utcnow()

        # Set the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        # Convert UTC time to Indian timezone
        indian_time = utc_now.replace(tzinfo=pytz.utc).astimezone(indian_timezone)

        # Format the time in 12-hour format
        indian_time_12hr = indian_time.strftime('%I:%M:%S %p')
        date = datetime.datetime.now().strftime('%d-%B-%Y')

        current_time = str(date + ' ' + indian_time_12hr)

        # Insert the username and time into the database along with the deletion action
        cursor.execute("INSERT INTO registers (username, login_time) VALUES (%s, %s)", (username, current_time))
        db.commit()

        return render_template('chat.html', username=username)

@app.route('/send_message', methods=['POST'])
def send_message():
    username = request.form['username']
    message = request.form['message']

    if message=='':
        return jsonify({'status': 'OK'})
    else:
        utc_now = datetime.datetime.utcnow()

        # Set the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        # Convert UTC time to Indian timezone
        indian_time = utc_now.replace(tzinfo=pytz.utc).astimezone(indian_timezone)

        # Format the time in 12-hour format
        time = indian_time.strftime('%I:%M %p')
        date = datetime.datetime.now().strftime('%d-%B-%Y')

        # Insert message into the database
        cursor.execute("INSERT INTO chats (username, msg, msg_time, msg_date) VALUES (%s, %s, %s, %s)", (username, message, time, date))
        db.commit()

        return jsonify({'status': 'OK'})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    cursor.execute("SELECT * FROM chats")
    messages = cursor.fetchall()
    return jsonify(messages)

@app.route('/delete_chats', methods=['POST'])
def delete_chats():
    try:
        username = request.form.get('username')

        # Get the current UTC time
        utc_now = datetime.datetime.utcnow()

        # Set the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        # Convert UTC time to Indian timezone
        indian_time = utc_now.replace(tzinfo=pytz.utc).astimezone(indian_timezone)

        # Format the time in 12-hour format
        indian_time_12hr = indian_time.strftime('%I:%M:%S %p')
        date = datetime.datetime.now().strftime('%d-%B-%Y')

        current_time=str(date+' '+indian_time_12hr)

        # Insert the username and time into the database along with the deletion action
        cursor.execute("INSERT INTO deletion_log (username, deletion_time) VALUES (%s, %s)", (username, current_time))
        db.commit()
        cursor.execute("DROP TABLE IF EXISTS chats")  # Drop the chats table
        db.commit()
        print('Chats table deleted successfully')
        cursor.execute("CREATE TABLE IF NOT EXISTS chats (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), msg TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci, msg_time VARCHAR(100), msg_date VARCHAR(100))")
        print('table created')
        return jsonify({'status': 'OK'})
    except Exception as e:
        print('Error deleting chats:', str(e))
        return jsonify({'status': 'Error', 'message': str(e)})



#personal room code
@app.route('/myroom_chat', methods=['POST'])
def myroom_chat():
    username = request.form['username']
    if username=='':
        return render_template('myroom_index.html',error='USE A NAME TO CHAT')
    else:
        print('myroom game started')

        print(session.get('count'))

        # Get the current UTC time
        utc_now = datetime.datetime.utcnow()

        # Set the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        # Convert UTC time to Indian timezone
        indian_time = utc_now.replace(tzinfo=pytz.utc).astimezone(indian_timezone)

        # Format the time in 12-hour format
        indian_time_12hr = indian_time.strftime('%I:%M:%S %p')
        date = datetime.datetime.now().strftime('%d-%B-%Y')

        current_time = str(date + ' ' + indian_time_12hr)
        print(session.get("count"))
        # Insert the username and time into the database along with the deletion action
        cursor.execute("INSERT INTO myroom_logs (username, login_time,room_name) VALUES (%s, %s,%s)", (username, current_time,f'room_{session.get("count")}'))
        db.commit()
        return render_template('myroom_chat.html', username=username)

@app.route('/send_myroom_message', methods=['POST'])
def send_myroom_message():
    username = request.form['username']
    message = request.form['message']

    if message=='':
        return jsonify({'status': 'OK'})
    else:
        utc_now = datetime.datetime.utcnow()

        # Set the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        # Convert UTC time to Indian timezone
        indian_time = utc_now.replace(tzinfo=pytz.utc).astimezone(indian_timezone)

        # Format the time in 12-hour format
        time = indian_time.strftime('%I:%M %p')
        date = datetime.datetime.now().strftime('%d-%B-%Y')
        # Insert message into the rooms
        cursor.execute(f"INSERT INTO room_{session.get('count')} (username, msg, msg_time, msg_date) VALUES (%s, %s, %s, %s)", (username, message, time, date))
        #inserting msg to myroom
        cursor.execute("INSERT INTO myroom_chats (username, msg, msg_time, msg_date) VALUES (%s, %s, %s, %s)", (username, message, time, date))
        db.commit()

        return jsonify({'status': 'OK'})


@app.route('/get_myroom_messages', methods=['GET'])
def get_myroom_messages():
    cursor.execute("SELECT * FROM myroom_chats")
    messages = cursor.fetchall()
    return jsonify(messages)


@app.route('/delete_myroom_chats', methods=['POST'])
def delete_myroom_chats():
    try:
        username = request.form.get('username')

        # Get the current UTC time
        utc_now = datetime.datetime.utcnow()

        # Set the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        # Convert UTC time to Indian timezone
        indian_time = utc_now.replace(tzinfo=pytz.utc).astimezone(indian_timezone)

        # Format the time in 12-hour format
        indian_time_12hr = indian_time.strftime('%I:%M:%S %p')
        date = datetime.datetime.now().strftime('%d-%B-%Y')

        current_time=str(date+' '+indian_time_12hr)

        # Insert the username and time into the database along with the deletion action
        cursor.execute("INSERT INTO myroom_deletion_log (username, deletion_time) VALUES (%s, %s)", (username, current_time))
        db.commit()
        cursor.execute("DROP TABLE IF EXISTS myroom_chats")  # Drop the chats table
        db.commit()
        print('Chats table deleted successfully')
        count = session.get('count')
        print(count)
        while True:
            try:
                # Check if the table exists
                cursor.execute(f"SELECT 1 FROM room_{count}")
                cursor.fetchall()  # Fetch all results to clear any pending results
                # If no exception is raised, it means the table exists
                count += 1  # Move to the next count
            except mysql.connector.Error as e:
                if e.errno == 1146:  # Table doesn't exist error code
                    # Create the table with the current count
                    print('creating table')
                    cursor.execute(
                        f"CREATE TABLE room_{count} (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), msg TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci, msg_time VARCHAR(100), msg_date VARCHAR(100))")
                    db.commit()
                    print('created table')
                    session['count'] = count  # Store the updated count in the session
                    break  # Exit the loop
                else:
                    # Handle other MySQL errors
                    print('errorfound+', str(e))

        cursor.execute("CREATE TABLE IF NOT EXISTS myroom_chats (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), msg TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci, msg_time VARCHAR(100), msg_date VARCHAR(100))")
        print('table created')
        return jsonify({'status': 'OK'})
    except Exception as e:
        print('Error deleting chats:', str(e))
        return jsonify({'status': 'Error', 'message': str(e)})


#master card
@app.route('/menu')
def menu():
        return render_template('menu.html')

@app.route('/view_deletes')
def view_deleted_chatuser():
        cursor.execute("SELECT * FROM deletion_log")
        messages = cursor.fetchall()
        return render_template('view_deletes.html',messages=messages)

@app.route('/view_users')
def view_users():
        cursor.execute("SELECT * FROM registers")
        messages = cursor.fetchall()
        return render_template('view_users.html',messages=messages)

#personal room special url
@app.route('/myroom_delete')
def view_deleted_myroom_chatuser():
        cursor.execute("SELECT * FROM myroom_deletion_log")
        messages = cursor.fetchall()
        return render_template('view_myroom_deletes.html',messages=messages)

@app.route('/myroom_users')
def view_myroom_users():
        cursor.execute("SELECT * FROM myroom_logs")
        messages = cursor.fetchall()
        return render_template('view_myroom_users.html',messages=messages)

@app.route('/view_rooms')
def view_rooms():
    try:
        # Fetch table names from the database
        cursor.execute("SHOW TABLES LIKE 'room_%'")
        rows = cursor.fetchall()
        rooms = [row[0] for row in rows]  # Extract table names from the result
        return render_template('view_rooms.html', rooms=rooms)
    except mysql.connector.Error as e:
        print(str(e))

@app.route('/room/<room_name>')
def view_room_data(room_name):
    try:
        # Fetch data from the specified room table
        cursor.execute(f"SELECT * FROM {room_name}")
        room_data = cursor.fetchall()
        return render_template('view_room_data.html', room_name=room_name, room_data=room_data)
    except mysql.connector.Error as e:
        print(str(e))

if __name__ == '__main__':
    app.run(debug=True)


