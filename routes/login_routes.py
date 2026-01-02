"""
Routes de connexion et d'inscription pour le jeu Tic-Tac-Toe.

Ce module enregistre les routes HTTP liées à la gestion des utilisateurs :
- Affichage de la page de login et d'inscription
- Connexion et création de comptes
- Déconnexion des utilisateurs
- Gestion des cookies pour l'identification

Toutes les interactions avec la base de données passent par la classe
UserDAO.
"""
from sanic.response import redirect
# Pour les templates jinja2 - pip install jinja2 sanic-ext
from sanic_ext import render
from classes.UserDAO import UserDAO

UNEXPECTED = "Une erreur inattendue s'est produite. Svp essayez de nouveau."


def register_login_routes(app):
    """Enregistre les routes de login, logout et inscription.

    Args:
        app (Sanic): Instance de l'application Sanic.
    """
    login_page = "login.html"

    @app.route('/login')
    async def login(request):
        """Affiche la page de connexion.

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Page HTML de login rendue.
        """
        return await render(
            login_page, context={"page": "login"}
        )

    @app.post('/login')
    async def login_handler(request):
        """Gère la soumission du formulaire de connexion.

        Vérifie le nom d'utilisateur et le mot de passe, crée des cookies
        pour l'identification si la connexion est réussie.

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Redirection vers la page principale
            si succès, sinon retour à la page de login avec un message.
        """
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            try:
                dao = UserDAO("tictactoe.db")
                user = dao.get_user(username, password)

                if user:
                    response = redirect("/")
                    response.add_cookie(
                        "username",
                        str(user["username"]),
                        secure=False,
                        httponly=True
                    )
                    response.add_cookie(
                        "id",
                        str(user["id"]),
                        secure=False,
                        httponly=True
                    )
                    return response

                else:
                    message = "Le nom d'utilisateur et/ou "
                    "le mot de passe sont erronés."

            except (dao.OperationalError, dao.DatabaseError):
                # Erreurs liées à SQLite
                message = UNEXPECTED

        else:
            message = "Svp vérifiez votre nom d'utilisateur "
            "et votre mot de passe et réessayer."

        return await render(
            login_page, context={"message": message, "page": "login"}
        )

    @app.route('/logout')
    async def logout(request):
        """Déconnecte l'utilisateur en supprimant les cookies.

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Redirection vers la page de login.
        """
        response = redirect("/login")
        response.delete_cookie("username")
        response.delete_cookie("id")
        return response

    @app.route('/register')
    async def register(request):
        """Affiche la page d'inscription.

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Page HTML de registre rendue.
        """
        return await render(
            login_page, context={"page": "register"}
        )

    @app.post('/register')
    async def register_handler(request):
        """Gère la soumission du formulaire d'inscription.

        Vérifie que le nom d'utilisateur et les mots de passe sont valides,
        que le mot de passe est confirmé et tente d'insérer l'utilisateur
        en base de données.

        Args:
            request (sanic.request.Request):
                Objet représentant la requête HTTP.

        Returns:
            sanic.response.HTTPResponse: Redirection vers la page de login
            si succès, sinon retour à la page d'inscription avec un message.
        """
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        message = None

        if len(username) > 2 and len(password) > 2 and password == password2:
            try:
                dao = UserDAO("tictactoe.db")
                uid = dao.insert_user(username, password)
                if uid > 0:
                    return redirect("/login")
                else:
                    message = "Ce nom d'utilisateur est déjà utilisé."
                    " Svp essayez de nouveau."

            except (dao.OperationalError, dao.DatabaseError):
                # Erreurs liées à SQLite
                message = UNEXPECTED

        else:
            message = "Le nom d'utilisateur et/ou le mot de passe "
            "ne rencontrent pas les demandes. Svp essayez de nouveau."

        return await render(
            login_page, context={"message": message, "page": "register"}
        )
