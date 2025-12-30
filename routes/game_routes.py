from sanic_ext import render # Pour les templates jinja2 - pip install jinja2 sanic-ext
from classes.LeaderboardHelper import LeaderboardHelper


def register_game_routes(app):

  @app.route('/')
  async def index(request):
      cookie_user = request.cookies.get("username")
      cookie_id = request.cookies.get("id")
      if cookie_user and cookie_id:
          return await render('game.html', context={"username": cookie_user})
      else:
          return await render(
              "login.html", context={"page": "login"}
          )

  @app.route('/leaderboard', methods=["GET", "POST"])
  async def leaderboard(request):
      game_result = None
      message = None

      lbh = LeaderboardHelper()
      lbh.set_leaderboard_file() # Mise à jour du tableau des meneurs.
      leaderboard_data = lbh.get_leaderboard_file()

      if type(leaderboard_data) is str:
          message = leaderboard_data
          leaderboard_data = None

      if request.method == "POST":
          game_result = request.form.get("result_value")

      return await render(
          "leaderboard.html", context={"leaders": leaderboard_data, "game_result": game_result, "message": message}
      )
