"""
Point d'entrée du serveur Tic-Tac-Toe avec Sanic.

Ce module initialise l'application Sanic, configure les routes
de l'application (jeu, login, WebSocket) et gère le démarrage
du serveur HTTP/HTTPS.

Fonctionnalités principales :
- Servir les fichiers statiques (HTML, JS, CSS)
- Initialiser l'objet Game pour gérer l'état de la partie
- Enregistrer les routes HTTP et WebSocket
- Démarrer le serveur en HTTP (ou HTTPS si SSL activé)
"""
from sanic import Sanic
from classes.Game import Game
from routes.game_routes import register_game_routes
from routes.login_routes import register_login_routes
from routes.websocket_routes import register_websocket_routes

# Création de l'application Sanic
app = Sanic("TicTacToe")

# Servir les fichiers statiques pour les chemins src="" dans le HTML
app.static('/', './')

# Configuration SSL pour HTTPS (certificat et clé privée)
ssl = {
    "cert": "../cert/fullchain.pem",
    "key": "../cert/privkey.pem",
}

# Initialisation de l'objet Game pour gérer l'état du plateau
game = Game()

# Enregistrement des routes
register_game_routes(app)
register_login_routes(app)
register_websocket_routes(app, game)


if __name__ == '__main__':
    # Démarrage du serveur HTTP
    app.run(host="127.0.0.1", port=8000)

    # Pour HTTPS :
    # Nécessite un certificat SSL et modification de game.js (wss et https)
    # Il est recommandé de mettre secure=True dans login_routes.py
    # app.run(host="0.0.0.0", port=8443, ssl=ssl)
