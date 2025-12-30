# tests/test_game_routes_simple.py
import unittest
from unittest.mock import patch
from sanic import Sanic
from sanic.response import text
from sanic_testing import TestManager
from routes import game_routes

class TestGameRoutes(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Create a fresh Sanic app for each test
        self.app = Sanic(f"test-app-{id(self)}")
        TestManager(self.app)

        # Register routes
        game_routes.register_game_routes(self.app)

    @patch("routes.game_routes.render")
    async def test_index_with_cookie(self, mock_render):
        mock_render.return_value = text("fake game page")

        headers = {"cookie": "username=Alice; id=1"}
        request, response = await self.app.asgi_client.get("/", headers=headers)

        mock_render.assert_called_with("game.html", context={"username": "Alice"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "fake game page")

    @patch("routes.game_routes.render")
    async def test_index_without_cookie(self, mock_render):
        mock_render.return_value = text("fake login page")

        request, response = await self.app.asgi_client.get("/")

        mock_render.assert_called_with("login.html", context={"page": "login"})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "fake login page")

    async def test_leaderboard_get(self):
        leaderboard_data = [{"username": "Alice", "points": 300}]

        with patch.object(game_routes.LeaderboardHelper, "set_leaderboard_file", return_value=None), \
             patch.object(game_routes.LeaderboardHelper, "get_leaderboard_file", return_value=leaderboard_data), \
             patch("routes.game_routes.render") as mock_render:

            mock_render.return_value = text("leaderboard page")

            request, response = await self.app.asgi_client.get("/leaderboard")

            mock_render.assert_called_with(
                "leaderboard.html",
                context={
                    "leaders": leaderboard_data,
                    "game_result": None,
                    "message": None
                }
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "leaderboard page")

    async def test_leaderboard_post_with_result(self):
        leaderboard_data = [{"username": "Alice", "points": 3}]
        data = {"result_value": "🎉 You WIN!"}

        with patch.object(game_routes.LeaderboardHelper, "set_leaderboard_file", return_value=None), \
             patch.object(game_routes.LeaderboardHelper, "get_leaderboard_file", return_value=leaderboard_data), \
             patch("routes.game_routes.render") as mock_render:

            mock_render.return_value = text("leaderboard post page")

            request, response = await self.app.asgi_client.post("/leaderboard", data=data)

            mock_render.assert_called_with(
                "leaderboard.html",
                context={
                    "leaders": leaderboard_data,
                    "game_result": "🎉 You WIN!",
                    "message": None
                }
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "leaderboard post page")

    async def test_leaderboard_post_without_result(self):
        leaderboard_data = [{"username": "Alice", "points": 300}]

        with patch.object(game_routes.LeaderboardHelper, "set_leaderboard_file", return_value=None), \
             patch.object(game_routes.LeaderboardHelper, "get_leaderboard_file", return_value=leaderboard_data), \
             patch("routes.game_routes.render") as mock_render:

            mock_render.return_value = text("leaderboard post page")

            request, response = await self.app.asgi_client.post("/leaderboard", data={})

            mock_render.assert_called_with(
                "leaderboard.html",
                context={
                    "leaders": leaderboard_data,
                    "game_result": None,
                    "message": None
                }
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "leaderboard post page")

    async def test_leaderboard_uses_leaderboard_file(self):
        leaderboard_data = [
            {"username": "Alice", "points": 300},
            {"username": "Bob", "points": 100},
        ]

        with patch.object(game_routes.LeaderboardHelper, "set_leaderboard_file", return_value=None), \
             patch.object(game_routes.LeaderboardHelper, "get_leaderboard_file", return_value=leaderboard_data), \
             patch("routes.game_routes.render") as mock_render:

            mock_render.return_value = text("leaderboard page")

            request, response = await self.app.asgi_client.get("/leaderboard")

            # Ensure the DAO method was called
            game_routes.LeaderboardHelper.get_leaderboard_file.assert_called_once()

            mock_render.assert_called_with(
                "leaderboard.html",
                context={
                    "leaders": leaderboard_data,
                    "game_result": None,
                    "message": None
                }
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "leaderboard page")

    @patch("routes.game_routes.render")
    @patch("routes.game_routes.LeaderboardHelper.get_leaderboard_file")
    async def test_leaderboard_file_missing(self, mock_get_file, mock_render):
        message = "Le tableau des meneurs n'est pas disponible en ce moment."

        mock_get_file.return_value = message
        mock_render.return_value = text("leaderboard page")

        request, response = await self.app.asgi_client.get("/leaderboard")

        mock_render.assert_called_with(
            "leaderboard.html",
            context={
                "leaders": None,
                "game_result": None,
                "message": message,
            }
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.text, "leaderboard page")

    async def test_leaderboard_post_with_result_and_file(self):
        leaderboard_data = [{"username": "Alice", "points": 500}]
        data = {"result_value": "🎉 Victoire !"}

        with patch.object(game_routes.LeaderboardHelper, "set_leaderboard_file", return_value=None), \
             patch.object(game_routes.LeaderboardHelper, "get_leaderboard_file", return_value=leaderboard_data), \
             patch("routes.game_routes.render") as mock_render:

            mock_render.return_value = text("leaderboard post page")

            request, response = await self.app.asgi_client.post("/leaderboard", data=data)

            mock_render.assert_called_with(
                "leaderboard.html",
                context={
                    "leaders": leaderboard_data,
                    "game_result": "🎉 Victoire !",
                    "message": None,
                }
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(response.text, "leaderboard post page")


if __name__ == "__main__":
    unittest.main()
