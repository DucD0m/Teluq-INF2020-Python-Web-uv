class WebsocketHelper:
    def __init__(self, game):
        self.game = game

    async def check_disconnect(self, ws, player_symbol):
        """
        Returns True if the game should be reset due to the other player disconnecting.
        """
        if player_symbol not in ("X", "O"):
            return False

        other_symbol = "O" if player_symbol == "X" else "X"

        if other_symbol not in self.game.connected.values():
            try:
                await ws.send(
                    "DISC|La connexion avec l'autre joueur a été perdue. La partie sera réinitialisée."
                )
            except (Exception, AttributeError):
                self.game.connected.pop(ws, None)

            self.game.reset_game()
            await self.broadcast(self.game.board_state())
            return True

        return False

    async def broadcast(self, message):
        """
        Send a message to all connected websockets. Remove disconnected ones.
        """
        for ws in list(self.game.connected.keys()):
            try:
                await ws.send(message)
            except (Exception, AttributeError):
                self.game.connected.pop(ws, None)

    async def close_all_connections(self):
        """
        Close all websocket connections safely and clear the connection dict.
        """
        for ws in list(self.game.connected.keys()):
            try:
                await ws.close()
            except (Exception, AttributeError):
                pass
            finally:
                self.game.connected.pop(ws, None)
