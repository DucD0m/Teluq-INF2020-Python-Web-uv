from sanic import Sanic, response
from classes.Game import Game
from routes.game_routes import register_game_routes
from routes.login_routes import register_login_routes
from routes.websocket_routes import register_websocket_routes

app = Sanic("TicTacToe")
app.static('/', './') #Pour les paths src="" dans le html.
game = Game()
login_page = "login.html"

register_game_routes(app, login_page)
register_login_routes(app, login_page)
register_websocket_routes(app, game)


if __name__ == '__main__':
    app.run()
