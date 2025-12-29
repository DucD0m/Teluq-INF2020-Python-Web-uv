class WebsocketHelper:

    def __init__(self, game):
        self.game = game

    async def check_disconnect(self, ws, player):
        """Retourne True si l'autre joueur a été déconnecté. Réinitialise la partie."""
        if player not in ("X", "O"):
            return False

        other_player = "O" if player == "X" else "X"

        if other_player not in self.game.connected.values():
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
        """Envoi un message à tous les websockets. Retire ceux qui ont été déconnectés."""
        for ws in list(self.game.connected.keys()):
            try:
                await ws.send(message)
            except (Exception, AttributeError):
                self.game.connected.pop(ws, None)

    async def close_all_connections(self):
        """Ferme toutes les connections et vide le dictionnaire des connexions."""
        for ws in list(self.game.connected.keys()):
            try:
                await ws.close()
            except (Exception, AttributeError):
                pass
            finally:
                self.game.connected.pop(ws, None)
