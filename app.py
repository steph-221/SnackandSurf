from flask import Flask, render_template, jsonify, request, redirect, url_for, session, abort
import sqlite3
import os
import subprocess

app = Flask(__name__)
app.secret_key = "super_secret_key_snack_surf"

DB_FILE = 'snack_menu.db'

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
        plats_defaut = [
            ("Burgers", "Classic Surf Burger", "4 000 FCFA", "Boeuf haché, cheddar, salade, tomate, sauce maison."),
            ("Boissons", "Smoothie Tropical", "2 500 FCFA", "Mélange mangue, ananas, fruit de la passion.")
        ]
        cursor.executemany('INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)', plats_defaut)
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/api/menu')
def get_menu():
    conn = get_db_connection()
    plats = conn.execute('SELECT * FROM menu').fetchall()
    conn.close()
    menu_data = {}
    for plat in plats:
        cat = plat['categorie']
        if cat not in menu_data:
            menu_data[cat] = {"categorie": cat, "items": []}
        menu_data[cat]["items"].append({
            "id": plat['id'],
            "nom": plat['nom'],
            "prix": plat['prix'],
            "desc": plat['description']
        })
    return jsonify(list(menu_data.values()))

ADMIN_PASSWORD = "surf"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' not in session:
        if request.method == 'POST':
            if request.form.get('password') == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                return redirect(url_for('admin'))
            else:
                return "Mot de passe incorrect", 403
        return render_template('admin_login.html')
    conn = get_db_connection()
    plats = conn.execute('SELECT * FROM menu ORDER BY categorie').fetchall()
    conn.close()
    return render_template('admin.html', plats=plats)

@app.route('/admin/ajouter', methods=['POST'])
def admin_ajouter():
    if 'admin_logged_in' not in session: return redirect(url_for('admin'))
    categorie = request.form['categorie']
    nom = request.form['nom']
    prix = request.form['prix']
    description = request.form['description']
    conn = get_db_connection()
    conn.execute('INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)', (categorie, nom, prix, description))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/supprimer/<int:id>', methods=['POST'])
def admin_supprimer(id):
    if 'admin_logged_in' not in session: return redirect(url_for('admin'))
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
    secret = request.args.get('token')
    if secret != "surf_secret_almadies_2026":
        abort(403)
    repo_dir = '/home/snackandsurf/SnackandSurf'
    
    # 1. Récupérer le code sur GitHub
    subprocess.run(['git', '-C', repo_dir, 'pull'], check=True)
    
    # 2. Recharger le serveur PythonAnywhere en actualisant le fichier WSGI
    wsgi_file = '/var/www/snackandsurf_pythonanywhere_com_wsgi.py'
    if os.path.exists(wsgi_file):
        os.utime(wsgi_file, None)
        
    return 'Site mis à jour avec succès !', 200

if __name__ == '__main__':
    app.run(debug=True)