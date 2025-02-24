from flask import Flask, render_template, request, redirect, url_for
from db_conn import get_db_connection

app = Flask(__name__)

# Route voor het ophalen van kamers
@app.route("/")
def kamers_overzicht():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT k.id, k.kamernummer, k.naam, k.capaciteit, k.tafelopstelling, k.beeldscherm, k.type,
               COALESCE(h.bedrijfsnaam, 'Niet verhuurd') AS huurder,
               c.startdatum, c.einddatum, c.status
        FROM kamers k
        LEFT JOIN contracten c ON k.id = c.kamer_id AND c.status = 'actief'
        LEFT JOIN huurders h ON c.huurder_id = h.id
        WHERE k.verwijderd = 0  -- Zorg ervoor dat soft-deleted kamers niet getoond worden
        ORDER BY k.kamernummer;
    """)
    
    kamers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template("index.html", kamers=kamers)


# Soft delete functie voor een contract
@app.route("/verwijderen/<int:kamer_id>")
def verwijder_contract(kamer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE kamers 
        SET verwijderd = 1
        WHERE id = %s
    """, (kamer_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for("kamers_overzicht"))


# Bewerken van een kamer
@app.route("/bewerken/<int:kamer_id>", methods=["GET", "POST"])
def bewerken(kamer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Haal kamergegevens op
    cursor.execute("""
        SELECT k.id, k.kamernummer, k.naam, k.capaciteit, k.tafelopstelling, k.beeldscherm, k.type,
               c.startdatum, c.einddatum, c.status, h.id AS huurder_id, h.bedrijfsnaam
        FROM kamers k
        LEFT JOIN contracten c ON k.id = c.kamer_id AND c.status = 'actief'
        LEFT JOIN huurders h ON c.huurder_id = h.id
        WHERE k.id = %s
    """, (kamer_id,))
    
    kamer = cursor.fetchone()
    
    if request.method == "POST":
        huurstatus = request.form['status']
        huurder_id = request.form['huurder']
        startdatum = request.form['startdatum']
        einddatum = request.form['einddatum']
        
        cursor.execute("""
            UPDATE contracten
            SET status = %s, huurder_id = %s, startdatum = %s, einddatum = %s
            WHERE kamer_id = %s AND status = 'actief'
        """, (huurstatus, huurder_id, startdatum, einddatum, kamer_id))
        
        conn.commit()
        return redirect(url_for("kamers_overzicht"))
    
    # Haal alle huurders op voor de dropdown
    cursor.execute("SELECT id, bedrijfsnaam FROM huurders")
    huurders = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("bewerken.html", kamer=kamer, huurders=huurders)

if __name__ == '__main__':
    app.run(debug=True)
