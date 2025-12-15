# tests/test_login_routes.py
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from sanic import Sanic
from sanic.response import text, redirect
from sanic_testing import TestManager
from routes import login_routes

class TestLoginRoutes(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Création d'une app unique par test
        self.app = Sanic(f"test-app-login-{id(self)}")
        TestManager(self.app)

        # Enregistre les routes avec page de login fictive
        login_routes.register_login_routes(self.app, login_page="login.html")

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    async def test_login_get(self, mock_render):
        mock_render.return_value = text("login page")
        _, response = await self.app.asgi_client.get("/login")

        mock_render.assert_awaited_with("login.html", context={"page": "login"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "login page")

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    @patch("routes.login_routes.UserDAO.get_user")
    async def test_login_post_success(self, mock_get_user, mock_render):
        mock_get_user.return_value = {"id": 1, "username": "Alice"}

        # Le render ne doit pas être appelé si connexion OK
        mock_render.return_value = text("unused")
        data = {"username": "Alice", "password": "1234"}

        _, response = await self.app.asgi_client.post("/login", data=data)

        self.assertEqual(response.status, 302)
        self.assertIn("/" , response.headers["location"])
        self.assertEqual(response.cookies["username"], "Alice")
        self.assertEqual(response.cookies["id"], "1")

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    @patch("routes.login_routes.UserDAO.get_user")
    async def test_login_post_failure_wrong_credentials(self, mock_get_user, mock_render):
        mock_get_user.return_value = None
        mock_render.return_value = text("login failed page")

        data = {"username": "Bob", "password": "wrong"}
        _, response = await self.app.asgi_client.post("/login", data=data)

        mock_render.assert_awaited()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "login failed page")

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    async def test_login_post_failure_missing_fields(self, mock_render):
        mock_render.return_value = text("login failed page")

        # username manquant
        data = {"password": "1234"}
        _, response = await self.app.asgi_client.post("/login", data=data)

        mock_render.assert_awaited()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "login failed page")

    async def test_logout(self):
        _, response = await self.app.asgi_client.get("/logout")
        self.assertEqual(response.status, 302)
        self.assertIn("/login", response.headers["location"])
        self.assertNotIn("username", response.cookies)
        self.assertNotIn("id", response.cookies)


    @patch("routes.login_routes.render", new_callable=AsyncMock)
    async def test_register_get(self, mock_render):
        mock_render.return_value = text("register page")
        _, response = await self.app.asgi_client.get("/register")

        mock_render.assert_awaited_with("login.html", context={"page": "register"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "register page")

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    @patch("routes.login_routes.UserDAO.insert_user")
    async def test_register_post_success(self, mock_insert_user, mock_render):
        mock_insert_user.return_value = 5
        mock_render.return_value = text("unused")

        data = {"username": "NewUser", "password": "1234", "password2": "1234"}
        _, response = await self.app.asgi_client.post("/register", data=data)

        self.assertEqual(response.status, 302)
        self.assertIn("/login", response.headers["location"])

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    @patch("routes.login_routes.UserDAO.insert_user")
    async def test_register_post_failure_existing_user(self, mock_insert_user, mock_render):
        mock_insert_user.return_value = 0
        mock_render.return_value = text("register failed page")

        data = {"username": "ExistingUser", "password": "1234", "password2": "1234"}
        _, response = await self.app.asgi_client.post("/register", data=data)

        mock_render.assert_awaited()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "register failed page")

    @patch("routes.login_routes.render", new_callable=AsyncMock)
    async def test_register_post_failure_invalid_input(self, mock_render):
        mock_render.return_value = text("register failed page")
        # mot de passe trop court ou mismatch
        data = {"username": "aa", "password": "1", "password2": "2"}
        _, response = await self.app.asgi_client.post("/register", data=data)

        mock_render.assert_awaited()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "register failed page")


if __name__ == "__main__":
    unittest.main()
