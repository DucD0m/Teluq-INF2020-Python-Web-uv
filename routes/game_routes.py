from sanic_ext import render # Pour les templates jinja2 - pip install jinja2 sanic-ext
from classes.GameDAO import GameDAO

def register_game_routes(app, login_page):

  @app.route('/')
  async def index(request):
      cookie_user = request.cookies.get("username")
      cookie_id = request.cookies.get("id")
      if cookie_user and cookie_id:
          return await render('game.html', context={"username": cookie_user})
      else:
          return await render(
              login_page, context={"page": "login"}
          )

  @app.route('/leaderboard', methods=["GET", "POST"])
  async def leaderboard(request):
      dao = GameDAO("tictactoe.db")
      leaders = dao.get_leaderboard()

      leaderboard_data = [
          {"username": row["username"], "wins": row["wins"]}
          for row in leaders
      ]

      game_result = None
      if request.method == "POST":
          game_result = request.form.get("result_value")

      return await render(
          "leaderboard.html", context={"leaders": leaderboard_data, "game_result": game_result}
      )
