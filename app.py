from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
import os
import subprocess

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
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM menu')
    if cursor.fetchone()[0] == 0:
        plats = [
            ("Burgers", "Classic Surf Burger", "4 000 FCFA", "Boeuf, cheddar, salade, tomate."),
            ("Boissons", "Smoothie Tropical", "2 500 FCFA", "Mangue, ananas, passion.")
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
    conn.close()
    return render_template('admin.html', plats=plats)

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
