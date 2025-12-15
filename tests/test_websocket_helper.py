import unittest
import asyncio

from classes.WebsocketHelper import WebsocketHelper

# Faux websocket pour les tests
class FakeWS:
    def __init__(self):
        self.sent = []
        self.closed = False

    async def send(self, message):
        self.sent.append(message)

    async def close(self):
        self.closed = True

# Faux Game pour injecter dans WebsocketHelper
class FakeGame:
    def __init__(self):
        self.connected = {}
        self.board = [""] * 9
        self.current_player = "X"

    def reset_game(self):
        self.board = [""] * 9
        self.current_player = "X"

    def board_state(self):
        return ",".join(self.board) + "|" + self.current_player

class TestWebsocketHelper(unittest.IsolatedAsyncioTestCase):

    async def test_check_disconnect_no_disconnect(self):
        """Pas de déconnexion → retourne False et n'envoie rien"""
        game = FakeGame()
        ws_x = FakeWS()
        ws_o = FakeWS()
        game.connected[ws_x] = "X"
        game.connected[ws_o] = "O"
        helper = WebsocketHelper(game)

        result = await helper.check_disconnect(ws_x, "X")
        self.assertFalse(result)
        self.assertEqual(ws_x.sent, [])
        self.assertEqual(ws_o.sent, [])

    async def test_check_disconnect_other_player_missing(self):
        """Autre joueur absent → retourne True et envoie DISC"""
        game = FakeGame()
        ws_x = FakeWS()
        game.connected[ws_x] = "X"  # seul joueur connecté
        helper = WebsocketHelper(game)

        result = await helper.check_disconnect(ws_x, "X")
        self.assertTrue(result)

        # Vérifie qu'au moins un message DISC a été envoyé
        self.assertTrue(any(msg.startswith("DISC|") for msg in ws_x.sent))

        # Vérifie que le jeu a été réinitialisé
        self.assertEqual(game.board, [""] * 9)
        self.assertEqual(game.current_player, "X")

    async def test_check_disconnect_spectator(self):
        """Spectateur → ne fait rien"""
        game = FakeGame()
        ws_s = FakeWS()
        game.connected[ws_s] = "S"
        helper = WebsocketHelper(game)

        result = await helper.check_disconnect(ws_s, "S")
        self.assertFalse(result)
        self.assertEqual(ws_s.sent, [])

    async def test_broadcast_multiple_ws(self):
        """Tous les websockets reçoivent le message"""
        game = FakeGame()
        ws_x = FakeWS()
        ws_o = FakeWS()
        game.connected[ws_x] = "X"
        game.connected[ws_o] = "O"
        helper = WebsocketHelper(game)

        await helper.broadcast("test message")
        self.assertIn("test message", ws_x.sent)
        self.assertIn("test message", ws_o.sent)

    async def test_close_all_connections(self):
        """Toutes les connections sont fermées et la liste cleared"""
        game = FakeGame()
        ws_x = FakeWS()
        ws_o = FakeWS()
        game.connected[ws_x] = "X"
        game.connected[ws_o] = "O"
        helper = WebsocketHelper(game)

        await helper.close_all_connections()
        self.assertTrue(ws_x.closed)
        self.assertTrue(ws_o.closed)
        self.assertEqual(game.connected, {})

if __name__ == "__main__":
    unittest.main()
