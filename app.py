import os
import subprocess
from flask import Flask, render_template, jsonify, request, abort

app = Flask(__name__)

# --- DONNÉES DU RESTAURANT (La Carte) ---
menu_data = [
    {"categorie": "Burgers", "items": [
        {"nom": "Classic Surf Burger", "prix": "4 000 FCFA", "desc": "Boeuf, cheddar, salade, tomate, sauce maison"},
        {"nom": "Chicken Beach", "prix": "3 500 FCFA", "desc": "Poulet croustillant, mayo épicée"}
    ]},
    {"categorie": "Hot-Dogs", "items": [
        {"nom": "New York Dog", "prix": "2 500 FCFA", "desc": "Saucisse boeuf, oignons frits, moutarde"}
    ]},
    {"categorie": "Douceurs", "items": [
        {"nom": "Gaufre Nutella", "prix": "2 000 FCFA", "desc": "Gaufre chaude, Nutella, chantilly"}
    ]}
]

# --- ROUTES DU SITE ---

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/api/menu')
def get_menu():
    return jsonify(menu_data)

# --- WEBHOOK POUR DÉPLOIEMENT AUTOMATIQUE ---
@app.route('/deploy', methods=['POST'])
def auto_deploy():
    # Vérification d'un mot de passe secret pour la sécurité
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