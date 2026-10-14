from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_snack_surf'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'snack_menu.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie TEXT NOT NULL,
            nom TEXT NOT NULL,
            prix TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_demande TEXT NOT NULL,
            nom TEXT NOT NULL,
            contact TEXT NOT NULL,
            date_event TEXT NOT NULL,
            personnes INTEGER NOT NULL,
            type_event TEXT NOT NULL,
            statut TEXT DEFAULT 'En attente'
        )
    ''')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM menu')
    if cursor.fetchone()[0] == 0:
        plats = [
            ("Menu du Jour", "Formule du Midi", "2500 FCFA", "Le Plat du Jour au choix (voir l'ardoise)"),
            ("Snacks", "Hot Dog Crispy", "2000 FCFA", "Saucisse, Mozza, Pate (corn dog), chapelure, oignons crispy. Sauces: Moutarde, Ketchup."),
            ("Snacks", "Hot Dog New York", "2500 FCFA", "2 Saucisses, choux cuit, oignons caramelises, pain hot dog. Sauces: Mayo, Moutarde, Ketchup."),
            ("Snacks", "Veggie Burger", "3500 FCFA", "Galette de pois chiche, poelee de champignons, tomate, fromage frais, pain burger, coleslaw."),
            ("Snacks", "Cheese Burger Steak", "4000 FCFA", "1 Steak, cheddar, oignons caramelises, tomate, roties, pain burger, coleslaw."),
            ("Snacks", "Corean Wings", "3000 FCFA", "Ailes de poulet croustillantes et dorees a la coreenne."),
            ("Sides", "Portion de Frites", "1000 FCFA", ""),
            ("Menus / Combo", "Combo Hot Dog Crispy", "3500 FCFA", "+ FRITES + BOISSON (Sucree, Jus Local ou Eau 0,5L)"),
            ("Menus / Combo", "Combo Hot Dog New York", "4000 FCFA", "+ FRITES + BOISSON (Sucree, Jus Local ou Eau 0,5L)"),
            ("Menus / Combo", "Combo Veggie Burger", "5000 FCFA", "+ FRITES + BOISSON (Sucree, Jus Local ou Eau 0,5L)"),
            ("Menus / Combo", "Combo Cheese Burger Steak", "5500 FCFA", "+ FRITES + BOISSON (Sucree, Jus Local ou Eau 0,5L)"),
            ("Crepes", "Crepe Sucree", "1500 FCFA", "Crepe douce au sucre fin."),
            ("Crepes", "Crepe Jambon Fromage", "2500 FCFA", "Jambon savoureux et fromage fondant."),
            ("Crepes", "Crepe Poulet Champignon Fromage", "3500 FCFA", "Emince de poulet, champignons et fromage fondant."),
            ("Crepes", "Crepes Veggi Champignons Legumes", "2500 FCFA", "Melange de legumes frais de saison et champignons sautes."),
            ("Gourmandises", "Gaufre Sucre Glace", "1500 FCFA", ""),
            ("Gourmandises", "Pancake Spaghetti Nature", "1500 FCFA", ""),
            ("Gourmandises", "Pancake Nature", "1500 FCFA", ""),
            ("Gourmandises", "Part de Cake Vanille", "1000 FCFA", ""),
            ("Gourmandises", "Part de Cake Chocolat", "1500 FCFA", ""),
            ("Boissons Chaudes", "Cafe American Alonge", "1000 FCFA", ""),
            ("Boissons Chaudes", "Cafe Expresso", "1500 FCFA", ""),
            ("Boissons Chaudes", "Cafe Latte", "1500 FCFA", ""),
            ("Boissons Chaudes", "Infusion / The", "1000 FCFA", ""),
            ("Boissons Fraiches", "Boissons Sucrees", "1000 FCFA", "Coca, Coca Zero, Sprite, Fanta, Schweppes"),
            ("Boissons Fraiches", "Jus Locaux", "1000 FCFA", "Bissap, Bouye (selon saison)"),
            ("Boissons Fraiches", "Eau Casamancaise 1,5L", "1000 FCFA", ""),
            ("Boissons Fraiches", "Eau Casamancaise 0.5L", "500 FCFA", ""),
            ("Glaces", "Creamy Fraise / Choco", "1000 FCFA", ""),
            ("Glaces", "Eskimo Vanille / Fraise", "1000 FCFA", ""),
            ("Glaces", "Eskimo Choco", "1000 FCFA", "")
        ]
        cursor.executemany('INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)', plats)
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def accueil(): 
    return render_template('index.html')

@app.route('/api/menu')
def get_menu():
    conn = get_db_connection()
    plats = conn.execute('SELECT * FROM menu ORDER BY categorie').fetchall()
    conn.close()
    menu = {}
    for p in plats:
        cat = p['categorie']
        if cat not in menu: 
            menu[cat] = {"categorie": cat, "items": []}
        menu[cat]["items"].append({
            "id": p['id'], 
            "nom": p['nom'], 
            "prix": p['prix'], 
            "desc": p['description']
        })
    return jsonify(list(menu.values()))

@app.route('/privatisation', methods=['GET', 'POST'])
def privatisation():
    succes = False
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        contact = request.form.get('email', '').strip() or request.form.get('contact', '').strip()
        date_event = request.form.get('date', '').strip()
        personnes_raw = request.form.get('personnes', '1')
        try:
            personnes = int(personnes_raw)
        except ValueError:
            personnes = 1
        type_event = request.form.get('type', '').strip()
        date_demande = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO reservations (date_demande, nom, contact, date_event, personnes, type_event, statut) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (date_demande, nom, contact, date_event, personnes, type_event, 'En attente')
        )
        conn.commit()
        conn.close()
        succes = True
    return render_template('privatisation.html', succes=succes)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' not in session:
        if request.method == 'POST':
            if request.form.get('password') == 'surf':
                session['admin_logged_in'] = True
                return redirect(url_for('admin'))
            return "Mot de passe incorrect", 403
        return render_template('admin_login.html')
    conn = get_db_connection()
    plats = conn.execute('SELECT * FROM menu ORDER BY categorie').fetchall()
    reservations = conn.execute('SELECT * FROM reservations ORDER BY date_demande DESC').fetchall()
    conn.close()
    return render_template('admin.html', plats=plats, reservations=reservations)

@app.route('/admin/ajouter', methods=['POST'])
def admin_ajouter():
    if 'admin_logged_in' not in session: 
        return redirect(url_for('admin'))
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)', 
        (request.form['categorie'], request.form['nom'], request.form['prix'], request.form['description'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/supprimer/<int:id>', methods=['POST'])
def admin_supprimer(id):
    if 'admin_logged_in' not in session: 
        return redirect(url_for('admin'))
    conn = get_db_connection()
    conn.execute('DELETE FROM menu WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/reservation/statut/<int:id>', methods=['POST'])
def admin_reservation_statut(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    nouveau_statut = request.form.get('statut', 'En attente')
    conn = get_db_connection()
    conn.execute('UPDATE reservations SET statut = ? WHERE id = ?', (nouveau_statut, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/reservation/supprimer/<int:id>', methods=['POST'])
def admin_reservation_supprimer(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    conn = get_db_connection()
    conn.execute('DELETE FROM reservations WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

@app.route('/deploy', methods=['POST'])
def auto_deploy():
    if request.args.get('token') != 'surf_secret_almadies_2026': 
        from flask import abort
        abort(403)
    subprocess.run(['git', '-C', '/home/snackandsurf/SnackandSurf', 'pull'], check=True)
    if os.path.exists('/var/www/snackandsurf_pythonanywhere_com_wsgi.py'): 
        os.utime('/var/www/snackandsurf_pythonanywhere_com_wsgi.py', None)
    return 'Site mis a jour', 200

if __name__ == '__main__': 
    app.run(debug=True)