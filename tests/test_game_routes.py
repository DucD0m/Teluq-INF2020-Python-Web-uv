# tests/test_game_routes_simple.py
import unittest
from unittest.mock import patch, AsyncMock
from sanic import Sanic
from sanic.response import text
from sanic_testing import TestManager
from routes import game_routes

class TestGameRoutes(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Crée une app Sanic unique par test
        self.app = Sanic(f"test-app-{id(self)}")
        TestManager(self.app)

        # Enregistre les routes
        game_routes.register_game_routes(self.app, login_page="login.html")

    @patch("routes.game_routes.render", new_callable=AsyncMock)
    async def test_index_with_cookie(self, mock_render):
        # render renvoie un vrai HTTPResponse
        mock_render.return_value = text("fake game page")

        headers = {"cookie": "username=Alice; id=1"}
        request, response = await self.app.asgi_client.get("/", headers=headers)

        mock_render.assert_awaited_with("game.html", context={"username": "Alice"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "fake game page")

    @patch("routes.game_routes.render", new_callable=AsyncMock)
    async def test_index_without_cookie(self, mock_render):
        mock_render.return_value = text("fake login page")

        request, response = await self.app.asgi_client.get("/")

        mock_render.assert_awaited_with("login.html", context={"page": "login"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "fake login page")

    @patch("routes.game_routes.render", new_callable=AsyncMock)
    @patch("routes.game_routes.GameDAO.get_leaderboard")
    async def test_leaderboard_get(self, mock_get_leaderboard, mock_render):
        mock_get_leaderboard.return_value = [{"username": "Alice", "wins": 3}]
        mock_render.return_value = text("leaderboard page")

        request, response = await self.app.asgi_client.get("/leaderboard")

        mock_render.assert_awaited_with(
            "leaderboard.html",
            context={"leaders": [{"username": "Alice", "wins": 3}], "game_result": None}
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "leaderboard page")

    @patch("routes.game_routes.render", new_callable=AsyncMock)
    @patch("routes.game_routes.GameDAO.get_leaderboard")
    async def test_leaderboard_post_with_result(self, mock_get_leaderboard, mock_render):
        mock_get_leaderboard.return_value = [{"username": "Alice", "wins": 3}]
        mock_render.return_value = text("leaderboard post page")

        data = {"result_value": "🎉 You WIN!"}
        request, response = await self.app.asgi_client.post("/leaderboard", data=data)

        mock_render.assert_awaited_with(
            "leaderboard.html",
            context={"leaders": [{"username": "Alice", "wins": 3}], "game_result": "🎉 You WIN!"}
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "leaderboard post page")

    @patch("routes.game_routes.render", new_callable=AsyncMock)
    @patch("routes.game_routes.GameDAO.get_leaderboard")
    async def test_leaderboard_post_without_result(self, mock_get_leaderboard, mock_render):
        mock_get_leaderboard.return_value = [{"username": "Alice", "wins": 3}]
        mock_render.return_value = text("leaderboard post page")

        request, response = await self.app.asgi_client.post("/leaderboard", data={})

        mock_render.assert_awaited_with(
            "leaderboard.html",
            context={"leaders": [{"username": "Alice", "wins": 3}], "game_result": None}
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "leaderboard post page")


if __name__ == "__main__":
    unittest.main()
