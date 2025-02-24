from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'jouw_geheime_sleutel'

# Database 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kamerverhuur'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kamers")
    kamers = cur.fetchall()
    cur.close()
    return render_template('index.html', kamers=kamers)

@app.route('/kamer_bewerken/<int:id>', methods=['GET', 'POST'])
def kamer_bewerken(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kamers WHERE id = %s", (id,))
    kamer = cur.fetchone()
    print(kamer[4])
    
    if request.method == 'POST':
        kamernummer = request.form['kamernummer']
        naam = request.form['naam']
        capaciteit = request.form['capaciteit']
        tafelopstelling = request.form['tafelopstelling']
        beeldscherm = request.form['beeldscherm']
        type_kamer = request.form['type']
        print(type_kamer)

        cur.execute("""
            UPDATE kamers SET kamernummer = %s, naam = %s, capaciteit = %s, 
            tafelopstelling = %s, beeldscherm = %s, type = %s WHERE id = %s
        """, (kamernummer, naam, capaciteit, tafelopstelling, beeldscherm, type_kamer, id))
        
        
        mysql.connection.commit()
        cur.close()

        flash('Kamer succesvol bijgewerkt!', 'success')
        return redirect(url_for('index'))
    
    cur.close()
    return render_template('kamer_bewerken.html', kamer=kamer)


@app.route('/zoeken', methods=['GET'])
def zoeken():
    zoekterm = request.args.get('q', '')

    cur = mysql.connection.cursor()
    query = "SELECT * FROM kamers WHERE naam LIKE %s OR kamernummer LIKE %s"
    cur.execute(query, ('%' + zoekterm + '%', '%' + zoekterm + '%'))
    kamers = cur.fetchall()
    cur.close()

    if not kamers:  # Controleer of er geen kamers zijn gevonden
        flash('Geen kamers gevonden met de opgegeven zoekterm.', 'danger')

    return render_template('index.html', kamers=kamers)



@app.route('/kamer_toevoegen', methods=['GET', 'POST'])
def kamer_toevoegen():
    if request.method == 'POST':
        kamernummer = request.form['kamernummer']
        naam = request.form['naam']
        capaciteit = request.form['capaciteit']
        tafelopstelling = request.form['tafelopstelling']
        beeldscherm = request.form['beeldscherm']
        type_kamer = request.form['type']

        cur = mysql.connection.cursor()
        
        # Check of kamer al bestaat
        cur.execute("SELECT * FROM kamers WHERE kamernummer = %s", (kamernummer,))
        existing_kamer = cur.fetchone()

        if existing_kamer:
            flash('Deze ruimte bestaat al!', 'danger')
            return redirect(url_for('kamer_toevoegen'))

        # voeg kamer toe
        cur.execute("INSERT INTO kamers (kamernummer, naam, capaciteit, tafelopstelling, beeldscherm, type) VALUES (%s, %s, %s, %s, %s, %s)",
                    (kamernummer, naam, capaciteit, tafelopstelling, beeldscherm, type_kamer))
        
        mysql.connection.commit()
        cur.close()

        flash('Kamer succesvol toegevoegd!', 'success')
        return redirect(url_for('index'))
    
    return render_template('kamer_toevoegen.html')


@app.route('/kamer/verwijderen/<int:id>', methods=['POST'])
def kamer_verwijderen(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM kamers WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Kamer succesvol verwijderd!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

