"""
Routes HTTP principales pour le jeu Tic-Tac-Toe.

Ce module enregistre les routes de l'application Sanic liées au jeu,
notamment la page d'accueil et le tableau des meneurs (leaderboard).

Fonctionnalités :
- Page d'accueil : vérifie les cookies et affiche le jeu ou la page de login
- Leaderboard : met à jour et affiche le top 10 des joueurs
"""
# Pour les templates jinja2 - pip install jinja2 sanic-ext
from sanic_ext import render
from classes.LeaderboardHelper import LeaderboardHelper


def register_game_routes(app):
    """Enregistre les routes liées au jeu Tic-Tac-Toe.

    Args:
        app (Sanic): Instance de l'application Sanic.
    """

    @app.route('/')
    async def index(request):
        """Page d'accueil.

        Vérifie les cookies pour déterminer si l'utilisateur est connecté.
        - Si connecté : affiche le plateau de jeu.
        - Sinon : affiche la page de connexion.

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Page HTML rendue.
        """
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
        """Page du leaderboard.

        Cette route :
        - Met à jour le tableau des meneurs à partir des résultats en base
        - Affiche le top 10 des joueurs
        - Gère l'affichage d'un message si le leaderboard n'est pas disponible
        - Permet de récupérer un résultat de partie envoyé via POST

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Page HTML rendue avec le contexte
                comprenant :
                - leaders : liste des joueurs et leurs points
                - game_result : résultat de la partie (si POST)
                - message : message d'erreur ou d'information
        """
        game_result = None
        message = None

        lbh = LeaderboardHelper()
        lbh.set_leaderboard_file()  # Mise à jour du tableau des meneurs.
        leaderboard_data = lbh.get_leaderboard_file()

        if type(leaderboard_data) is str:
            message = leaderboard_data
            leaderboard_data = None

        if request.method == "POST":
            game_result = request.form.get("result_value")

        return await render(
            "leaderboard.html",
            context={
                "leaders": leaderboard_data,
                "game_result": game_result,
                "message": message
            }
        )
