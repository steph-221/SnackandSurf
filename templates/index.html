<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snack and Surf - Almadies</title>
    <!-- Chargement de Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-800 font-sans relative">

    <!-- Navigation -->
    <nav class="bg-white shadow-md fixed w-full z-20 top-0">
        <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
            <a href="#" class="text-2xl font-bold text-blue-600">🏄‍♂️ Snack & Surf</a>
            <ul class="flex space-x-6 text-sm font-semibold">
                <li><a href="#accueil" class="hover:text-blue-500">Accueil</a></li>
                <li><a href="#carte" class="hover:text-blue-500">La Carte</a></li>
            </ul>
        </div>
    </nav>

    <!-- Section Hero (Accueil) -->
    <header id="accueil" class="mt-16 bg-blue-100 h-96 flex flex-col justify-center items-center text-center px-4" 
            style="background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1953&q=80'); background-size: cover; background-position: center;">
        <div class="bg-white bg-opacity-90 p-8 rounded-lg shadow-lg max-w-lg">
            <h1 class="text-4xl font-extrabold text-gray-900 mb-3">La pause gourmande des Almadies</h1>
            <p class="text-gray-700 mb-6">Burgers, Hot-dogs, Gaufres et Glaces face à la mer.</p>
            <a href="#carte" class="bg-blue-600 text-white px-6 py-3 rounded-full font-bold hover:bg-blue-700 transition">Voir le Menu</a>
        </div>
    </header>

    <!-- Section Carte (Générée par JavaScript) -->
    <section id="carte" class="max-w-6xl mx-auto px-4 py-16">
        <h2 class="text-3xl font-bold text-center mb-10 text-blue-600">Notre Carte</h2>
        <div id="menu-container" class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Le menu s'affiche ici dynamiquement -->
        </div>
    </section>

    <!-- Pied de page -->
    <footer class="bg-gray-800 text-white text-center py-6 mb-16 sm:mb-0">
        <p>📍 Route Corniche Almadies | 📞 +221 71 057 93 71 | ✉️ contact@snackandsurf.sn</p>
    </footer>

    <!-- Bouton Flottant WhatsApp -->
    <a href="https://wa.me/221710579371?text=Bonjour%20Snack%20%26%20Surf%2C%20je%20souhaite%20passer%20commande%20ou%20avoir%20des%20informations%20!"
       target="_blank"
       rel="noopener noreferrer"
       class="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3 px-5 rounded-full shadow-2xl transition-all transform hover:scale-105"
       aria-label="Discuter sur WhatsApp">
        <!-- Icône officielle WhatsApp en SVG -->
        <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
            <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.599 2.679-.702c.97.529 1.838.783 2.78.783h.001c3.182 0 5.768-2.587 5.769-5.766.001-3.182-2.585-5.767-5.769-5.767zm7.551 5.766c-.001 4.165-3.39 7.554-7.553 7.554-1.259 0-2.438-.328-3.486-.902l-4.543 1.19 1.213-4.431c-.655-1.084-1.024-2.353-1.024-3.411.001-4.165 3.39-7.554 7.553-7.554 4.164 0 7.553 3.389 7.554 7.554zm-4.708 2.062c-.21-.105-1.242-.613-1.434-.683-.193-.07-.333-.105-.473.105-.14.21-.543.683-.666.823-.122.14-.245.158-.455.053-.21-.105-.888-.327-1.691-1.043-.625-.558-1.047-1.247-1.17-1.457-.122-.21-.013-.324.092-.428.095-.094.21-.245.315-.368.105-.123.14-.21.21-.35.07-.14.035-.263-.018-.368-.053-.105-.473-1.14-.648-1.56-.17-.41-.344-.354-.473-.36-.122-.006-.263-.007-.403-.007-.14 0-.368.053-.56.263-.193.21-.736.719-.736 1.753s.753 2.033.858 2.173c.105.14 1.482 2.263 3.59 3.173.501.217.892.346 1.197.443.503.16 1.012.137 1.393.08.425-.064 1.242-.508 1.417-.999.175-.49.175-.91.122-.999-.052-.088-.192-.14-.402-.245z"/>
        </svg>
        <span class="font-medium text-sm">Commander</span>
    </a>

    <!-- Script JavaScript pour charger les données du menu -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('/api/menu')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('menu-container');
                    data.forEach(categorie => {
                        let html = `<div class="bg-white p-6 rounded-lg shadow-md border-t-4 border-blue-500">`;
                        html += `<h3 class="text-2xl font-bold mb-4 border-b pb-2 text-gray-800">${categorie.categorie}</h3>`;
                        categorie.items.forEach(item => {
                            html += `
                                <div class="mb-4">
                                    <div class="flex justify-between font-bold text-lg">
                                        <span>${item.nom}</span>
                                        <span class="text-blue-600">${item.prix}</span>
                                    </div>
                                    <p class="text-gray-500 text-sm mt-1">${item.desc}</p>
                                </div>
                            `;
                        });
                        html += `</div>`;
                        container.innerHTML += html;
                    });
                });
        });
    </script>
</body>
</html>