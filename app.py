from sanic import Sanic, response
from classes.Game import Game
from routes.game_routes import register_game_routes
from routes.login_routes import register_login_routes
from routes.websocket_routes import register_websocket_routes

app = Sanic("TicTacToe")
app.static('/', './') #Pour les paths src="" dans le html.

## Localisation des certificats SSL.
ssl = {
"cert": "../cert/fullchain.pem",
"key": "../cert/privkey.pem",
}

game = Game()

register_game_routes(app)
register_login_routes(app)
register_websocket_routes(app, game)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000) #http

    ## HTTPS -> Besoin d'un certificat ssl et de modifier game.js (wss et https au lieu de ws et http).
    ## Il est souhaitable de mettre secure = True dans login_routes.py
    # app.run(host="0.0.0.0", port=8443, ssl=ssl) #https
