from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

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

@app.route('/')
def showData():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kamers")
    data = cursor.fetchall()
    data = replace_none_with_empty(data)
    cursor.close()
    conn.close()

    return render_template('showdata.html', data=data)

@app.route('/edit/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        kamernummer = request.form['kamernummer']
        naam = request.form['naam']
        capaciteit = request.form['capaciteit']
        tafelopstelling = request.form['tafelopstelling']
        beeldscherm = request.form['beeldscherm']
        type = request.form['type']
        
        cursor.execute("""
            UPDATE kamers
            SET kamernummer = %s, naam = %s, capaciteit = %s, tafelopstelling = %s, beeldscherm = %s, type = %s
            WHERE id = %s
        """, (kamernummer, naam, capaciteit, tafelopstelling, beeldscherm, type, room_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('showData'))
    
    cursor.execute("SELECT * FROM kamers WHERE id = %s", (room_id,))
    room = cursor.fetchone()
    room = replace_none_with_empty(room)
    cursor.close()
    conn.close()
    
    return render_template('editroom.html', room=room)

@app.route('/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        kamernummer = request.form['kamernummer']
        naam = request.form['naam']
        capaciteit = request.form['capaciteit']
        tafelopstelling = request.form['tafelopstelling']
        beeldscherm = request.form['beeldscherm']
        type = request.form['type']
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO kamers (kamernummer, naam, capaciteit, tafelopstelling, beeldscherm, type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (kamernummer, naam, capaciteit, tafelopstelling, beeldscherm, type))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('showData'))
    
    return render_template('addroom.html')

@app.route('/delete/<int:room_id>', methods=['GET'])
def delete_room(room_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kamers WHERE id = %s", (room_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('showData'))

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
