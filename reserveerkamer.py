from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "kamerverhuur",
}

def create_connection():
    return mysql.connector.connect(**db_config)

def replace_none_with_empty(data):
    if isinstance(data, dict):
        return {k: (v if v is not None else '') for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_none_with_empty(item) for item in data]
    return data

app = Flask(__name__)
app.config['DEBUG'] = True  # Enable debug mode

@app.route('/reserveer')
def showData():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kamers")
    roomdata = cursor.fetchall()
    roomdata = replace_none_with_empty(roomdata)
    cursor.close()
    conn.close()

    return render_template('reserveerdata.html', roomdata=roomdata)

@app.route('/reserve', methods=['GET', 'POST'])
def reserve_room():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        room_id = request.form['room_id']
        user_id = request.form['user_id']
        aantal_personen = request.form['aantal_personen']
        startdatum = request.form['startdatum']
        einddatum = request.form['einddatum']
        
        cursor.execute("""
            INSERT INTO reserveringen (kamer_id, huurder_id, aantal_personen, startdatum, einddatum, status)
            VALUES (%s, %s, %s, %s, %s, 'actief')
        """, (room_id, user_id, aantal_personen, startdatum, einddatum))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('showData'))
    
    cursor.execute("SELECT * FROM kamers")
    roomdata = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('reserveerdata.html', roomdata=roomdata)

@app.route('/check_availability', methods=['POST'])
def check_availability():
    date = request.form['date']
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT kamers.*
        FROM kamers
        LEFT JOIN reserveringen ON kamers.id = reserveringen.kamer_id
        AND reserveringen.startdatum <= %s AND reserveringen.einddatum >= %s
        WHERE reserveringen.id IS NULL
    """, (date, date))
    
    available_rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('reserveerdata.html', roomdata=available_rooms, selected_date=date)

@app.route('/')
def reserved_rooms():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reserveringen.id, kamers.kamernummer, kamers.naam, reserveringen.aantal_personen, reserveringen.startdatum, reserveringen.einddatum, reserveringen.status
        FROM reserveringen
        JOIN kamers ON reserveringen.kamer_id = kamers.id
    """)
    reserved_rooms = cursor.fetchall()
    reserved_rooms = replace_none_with_empty(reserved_rooms)
    cursor.close()
    conn.close()

    return render_template('reservedrooms.html', reserved_rooms=reserved_rooms)

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
