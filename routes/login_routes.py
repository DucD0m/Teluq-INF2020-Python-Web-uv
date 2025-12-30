from sanic.response import redirect
from sanic_ext import render # Pour les templates jinja2 - pip install jinja2 sanic-ext
from classes.UserDAO import UserDAO


def register_login_routes(app):

    login_page = "login.html"
    UNEXPECTED = "Une erreur inattendue s'est produite. Svp essayez de nouveau."

    @app.route('/login')
    async def login(request):
        return await render(
            login_page, context={"page": "login"}
        )

    @app.post('/login')
    async def login_handler(request):

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
                    message = "Le nom d'utilisateur et/ou le mot de passe sont erronés."

            except:
                message = UNEXPECTED

        else:
            message = "Svp vérifiez votre nom d'utilisateur et votre mot de passe et réessayer."

        return await render(
            login_page, context={"message": message, "page": "login"}
        )

    @app.route('/logout')
    async def logout(request):
        response = redirect("/login")
        response.delete_cookie("username")
        response.delete_cookie("id")
        return response

    @app.route('/register')
    async def register(request):
        return await render(
            login_page, context={"page": "register"}
        )

    @app.post('/register')
    async def register_handler(request):

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
                    message = "Ce nom d'utilisateur est déjà utilisé. Svp essayez de nouveau."

            except:
                message = UNEXPECTED

        else:
            message = "Le nom d'utilisateur et/ou le mot de passe ne rencontrent pas les demandes. Svp essayez de nouveau."

        return await render(
            login_page, context={"message": message, "page": "register"}
        )
