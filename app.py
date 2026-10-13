from flask import Flask, render_template, jsonify

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

if __name__ == '__main__':
    app.run(debug=True)