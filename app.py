from sanic import Sanic, response
from classes.Game import Game
from routes.game_routes import register_game_routes
from routes.login_routes import register_login_routes
from routes.websocket_routes import register_websocket_routes

app = Sanic("TicTacToe")
app.static('/', './') #Pour les paths src="" dans le html.

ssl = {
"cert": "../cert/fullchain.pem",
"key": "../cert/privkey.pem",
}

game = Game()
login_page = "login.html"

register_game_routes(app, login_page)
register_login_routes(app, login_page)
register_websocket_routes(app, game)


if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=8000) #http

    # Besoin d'un certificat ssl et de modiffier game.js wss et https.
    app.run(host="10.0.1.13", port=8443, ssl=ssl) #https
