from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
import sqlite3
import os
import subprocess
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'super_secret_key_snack_surf'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'snack_menu.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

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
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO reservations (date_demande, nom, contact, date_event, personnes, type_event) VALUES (?, ?, ?, ?, ?, ?)', 
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.form.get('nom'), request.form.get('email'), request.form.get('date'), request.form.get('personnes'), request.form.get('type'))
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
    if 'admin_logged_in' not in session: return redirect(url_for('admin'))
    conn = get_db_connection()
    conn.execute('INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)', (request.form['categorie'], request.form['nom'], request.form['prix'], request.form['description']))
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

@app.route('/admin/reservation/statut/<int:id>', methods=['POST'])
def admin_reservation_statut(id):
    if 'admin_logged_in' not in session: return redirect(url_for('admin'))
    conn = get_db_connection()
    conn.execute('UPDATE reservations SET statut = ? WHERE id = ?', (request.form.get('statut'), id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/reservation/supprimer/<int:id>', methods=['POST'])
def admin_reservation_supprimer(id):
    if 'admin_logged_in' not in session: return redirect(url_for('admin'))
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
    if request.args.get('token') != 'surf_secret_almadies_2026': from flask import abort; abort(403)
    subprocess.run(['git', '-C', '/home/snackandsurf/SnackandSurf', 'pull'], check=True)
    if os.path.exists('/var/www/snackandsurf_pythonanywhere_com_wsgi.py'): os.utime('/var/www/snackandsurf_pythonanywhere_com_wsgi.py', None)
    return 'Site mis a jour', 200

if __name__ == '__main__': 
    app.run(debug=True)