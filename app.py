from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
import sqlite3
import json
import os
import subprocess
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder='static')
app.secret_key = 'super_secret_key_snack_surf'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'snack_menu.db')

# --- CONFIGURATION EMAIL WORKSPACE ---
EMAIL_SENDER = "contact@snackandsurf.sn"
EMAIL_PASSWORD = "sbcxdcpheyocrenh"
EMAIL_RECEIVER = "contact@snackandsurf.sn"

def send_notification_email(nom, contact, date_event, personnes, type_event, message_libre):
    sujet = f"🏖️ Nouvelle Privatisation Snack & Surf : {type_event} - {nom}"
    corps = f"""
Bonjour,

Une nouvelle demande de privatisation vient d'être effectuée sur le site Snack & Surf.

=====================================
Détails de la demande :
=====================================
• Nom / Entreprise : {nom}
• Contact (Email ou Tel) : {contact}
• Type d'événement : {type_event}
• Date souhaitée : {date_event}
• Nombre de personnes : {personnes}

Message du client :
{message_libre if message_libre else "Aucun message particulier."}
=====================================

Vous pouvez gérer cette demande dans votre panneau d'administration :
https://snackandsurf.sn/admin

Cordialement,
Le bot Snack & Surf
    """

    msg = MIMEMultipart()
    msg['From'] = f"Snack & Surf Web <{EMAIL_SENDER}>"
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = sujet
    msg.attach(MIMEText(corps, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email envoyé avec succès.")
    except Exception as e:
        print(f"Erreur d'envoi de l'email : {e}")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

SEED_FILE = os.path.join(BASE_DIR, 'menu_seed.json')

# Cree les tables si besoin et remplit la carte depuis menu_seed.json quand elle est vide
def upgrade_db():
    conn = get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie TEXT NOT NULL,
            nom TEXT NOT NULL,
            prix TEXT NOT NULL,
            description TEXT
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_demande TEXT NOT NULL,
            nom TEXT NOT NULL,
            contact TEXT NOT NULL,
            date_event TEXT NOT NULL,
            personnes INTEGER NOT NULL,
            type_event TEXT NOT NULL,
            statut TEXT DEFAULT 'En attente',
            message TEXT
        )''')
        try:
            conn.execute('ALTER TABLE reservations ADD COLUMN message TEXT')
        except sqlite3.OperationalError:
            pass # La colonne existe deja
        if conn.execute('SELECT COUNT(*) FROM menu').fetchone()[0] == 0 and os.path.exists(SEED_FILE):
            with open(SEED_FILE, encoding='utf-8') as f:
                for p in json.load(f):
                    conn.execute('INSERT INTO menu (categorie, nom, prix, description) VALUES (?, ?, ?, ?)',
                                 (p['categorie'], p['nom'], p['prix'], p['description']))
        conn.commit()
    finally:
        conn.close()

upgrade_db()

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
        nom = request.form.get('nom')
        contact = request.form.get('email')
        date_event = request.form.get('date')
        personnes = request.form.get('personnes')
        type_event = request.form.get('type')
        message_libre = request.form.get('message')
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO reservations (date_demande, nom, contact, date_event, personnes, type_event, message) VALUES (?, ?, ?, ?, ?, ?, ?)', 
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nom, contact, date_event, personnes, type_event, message_libre)
        )
        conn.commit()
        conn.close()
        
        send_notification_email(nom, contact, date_event, personnes, type_event, message_libre)
        succes = True
        
    return render_template('privatisation.html', succes=succes)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' not in session:
        if request.method == 'POST':
            if request.form.get('password') == 'Surf2026*':
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
    if request.args.get('token') != 'surf_secret_almadies_2026': 
        from flask import abort
        abort(403)
    repo = '/home/snackandsurf/SnackandSurf'
    try:
        subprocess.run(['git', '-C', repo, 'checkout', '--', '.'], capture_output=True)
        subprocess.run(['git', '-C', repo, 'pull'], check=True, capture_output=True)
        wsgi_file = '/var/www/snackandsurf_pythonanywhere_com_wsgi.py'
        if os.path.exists(wsgi_file): 
            os.utime(wsgi_file, None)
        return 'Site mis a jour avec succes !', 200
    except Exception as e:
        return f'Erreur deploy: {str(e)}', 500

if __name__ == '__main__': 
    app.run(debug=True)