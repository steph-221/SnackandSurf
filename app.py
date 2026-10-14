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
    current_count = cursor.fetchone()[0]
    
    # Si la base est vide ou contient seulement les 2 plats de test initiaux, on réinjecte toute la carte
    if current_count < 10:
        conn.execute('DELETE FROM menu')
        plats = [
            ('Menu du Jour', 'FORMULE DU MIDI', '2500 FCFA', '✨ Le Plat du Jour au choix (voir l\'ardoise)'),
            ('Snacks', 'HOT DOG CRISPY', '2000 FCFA', 'Saucisse, Mozza, Pâte (corn dog), chapelure, oignons crispy. Sauces: Moutarde, Ketchup.'),
            ('Snacks', 'HOT DOG NEW YORK', '2500 FCFA', '2 Saucisses, choux cuit, oignons caramélisés, pain hot dog. Sauces: Mayo, Moutarde, Ketchup.'),
            ('Snacks', 'VEGGIE BURGER', '3500 FCFA', 'Galette de pois chiche, poêlée de champignons, tomate, fromage frais, pain burger, coleslaw. Sauces: Mayo, Moutarde, Ketchup.'),
            ('Snacks', 'CHEESE BURGER STEAK', '4000 FCFA', '1 Steak, cheddar, oignons caramélisés, tomate, rôties, pain burger, coleslaw. Sauces: Mayo, Moutarde, Ketchup.'),
            ('Snacks', 'COREAN WINGS', '3000 FCFA', 'Ailes de poulet croustillantes et dorées à la coréenne.'),
            ('Snacks - Toppings Burger', '-- Topping Fromage', '500 FCFA', ''),
            ('Snacks - Toppings Burger', '-- Topping Œuf', '500 FCFA', ''),
            ('Snacks - Toppings Burger', '-- Topping Steak Sup.', '1000 FCFA', ''),
            ('Sides', 'PORTION DE FRITES', '1000 FCFA', ''),
            ('Menus / Combo', 'COMBO HOT DOG CRISPY', '3500 FCFA', '✨ + FRITES + BOISSON (Sucrée, Jus Local ou Eau 0,5L)'),
            ('Menus / Combo', 'COMBO HOT DOG NEW YORK', '4000 FCFA', '✨ + FRITES + BOISSON (Sucrée, Jus Local ou Eau 0,5L)'),
            ('Menus / Combo', 'COMBO VEGGIE BURGER', '5000 FCFA', '✨ + FRITES + BOISSON (Sucrée, Jus Local ou Eau 0,5L)'),
            ('Menus / Combo', 'COMBO CHEESE BURGER STEAK', '5500 FCFA', '✨ + FRITES + BOISSON (Sucrée, Jus Local ou Eau 0,5L)'),
            ('Crêpes', 'CRÊPE SUCRÉE', '1500 FCFA', 'Crêpe douce au sucre fin.'),
            ('Crêpes - Toppings', '-- Topping Chantilly', '500 FCFA', ''),
            ('Crêpes - Toppings', '-- Topping Confitures', '500 FCFA', ''),
            ('Crêpes - Toppings', '-- Topping Miel', '500 FCFA', ''),
            ('Crêpes - Toppings', '-- Topping Boule de Glace', '500 FCFA', ''),
            ('Crêpes - Toppings', '-- Topping Chocolat', '500 FCFA', ''),
            ('Crêpes - Toppings', '-- Topping Nutella', '1000 FCFA', ''),
            ('Crêpes', 'CRÊPE JAMBON FROMAGE', '2500 FCFA', 'Jambon savoureux et fromage fondant.'),
            ('Crêpes', 'CRÊPE POULET CHAMPIGNON FROMAGE', '3500 FCFA', 'Émincé de poulet, champignons et fromage fondant.'),
            ('Crêpes', 'CRÊPES VEGGI CHAMPIGNONS LÉGUMES', '2500 FCFA', 'Mélange de légumes frais de saison et champignons sautés.'),
            ('Crêpes - Options Salées', '-- Option Œuf', '500 FCFA', ''),
            ('Gourmandises / IHOP', 'GAUFRE SUCRE GLACE', '1500 FCFA', ''),
            ('Gourmandises / IHOP', 'PANCAKE SPAGHETTI NATURE', '1500 FCFA', ''),
            ('Gourmandises / IHOP', 'PANCAKE NATURE', '1500 FCFA', ''),
            ('Gourmandises - Toppings', '-- Topping Chantilly', '500 FCFA', ''),
            ('Gourmandises - Toppings', '-- Topping Confitures', '500 FCFA', ''),
            ('Gourmandises - Toppings', '-- Topping Miel', '500 FCFA', ''),
            ('Gourmandises - Toppings', '-- Topping Boule de Glace', '500 FCFA', ''),
            ('Gourmandises - Toppings', '-- Topping Chocolat', '500 FCFA', ''),
            ('Gourmandises - Toppings', '-- Topping Nutella', '1000 FCFA', ''),
            ('Gourmandises / IHOP', 'PART DE CAKE VANILLE', '1000 FCFA', ''),
            ('Gourmandises / IHOP', 'PART DE CAKE CHOCOLAT', '1500 FCFA', ''),
            ('Boissons Chaudes', 'CAFÉ AMERICAN ALONGÉ', '1000 FCFA', ''),
            ('Boissons Chaudes', 'CAFÉ EXPRESSO', '1500 FCFA', ''),
            ('Boissons Chaudes', 'CAFÉ LATTE', '1500 FCFA', ''),
            ('Boissons Chaudes', 'INFUSION / THÉ', '1000 FCFA', ''),
            ('Boissons Fraîches', 'BOISSONS SUCRÉES', '1000 FCFA', 'Coca, Coca Zéro, Sprite, Fanta, Schweppes'),
            ('Boissons Fraîches', 'JUS LOCAUX', '1000 FCFA', 'Bissap, Bouye (selon saison)'),
            ('Boissons Fraîches', 'EAU CASAMANCAISE 1,5L', '1000 FCFA', ''),
            ('Boissons Fraîches', 'EAU CASAMANCAISE 0.5L', '500 FCFA', ''),
            ('Glaces', 'CREAMY FRAISE / CHOCO', '1000 FCFA', ''),
            ('Glaces', 'ESKIMO VANILLE / FRAISE', '1000 FCFA', ''),
            ('Glaces', 'ESKIMO CHOCO', '1000 FCFA', '')
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
    plats = conn.execute('SELECT * FROM menu ORDER BY id').fetchall()
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
    plats = conn.execute('SELECT * FROM menu ORDER BY id').fetchall()
    reservations = conn.execute('SELECT * FROM reservations ORDER BY date_demande DESC').fetchall()
    conn.close()
    return render_template('admin.html', plats=plats, reservations=reservations)

@app.route('/admin/ajouter', methods=['POST'])
def admin_ajouter():
    if 'admin_logged_in' not in session: 
        return redirect(url_for('admin'))
    categorie = request.form.get('categorie', '').strip()
    if categorie == '__NEW__':
        categorie = request.form.get('nouvelle_categorie', '').strip()
    nom = request.form.get('nom', '').strip()
    prix = request.form.get('prix', '').strip()
    description = request.form.get('description', '').strip()

    if categorie and nom and prix:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)', 
            (categorie, nom, prix, description)
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
    repo = '/home/snackandsurf/SnackandSurf'
    subprocess.run(['git', '-C', repo, 'stash'], capture_output=True)
    subprocess.run(['git', '-C', repo, 'pull'], check=True)
    if os.path.exists('/var/www/snackandsurf_pythonanywhere_com_wsgi.py'): 
        os.utime('/var/www/snackandsurf_pythonanywhere_com_wsgi.py', None)
    return 'Site mis a jour', 200

from flask import send_from_directory

@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.root_path, request.path[1:])

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, request.path[1:])

if __name__ == '__main__': 
    app.run(debug=True)