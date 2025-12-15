class WebsocketHelper:

    def __init__(self, game):
        self.game = game

    async def check_disconnect(self, ws, player_symbol):
        """Retourne True si la partie doit être réinitialisée pour déconnexion de l'autre joueur."""
        if player_symbol not in ("X", "O"):
            return False

        other_symbol = "O" if player_symbol == "X" else "X"

        if other_symbol not in self.game.connected.values():
            await ws.send("DISC|" + "La connection avec l'autre joueur a été perdue. La partie sera réinitialisée.")
            # self.game.board = [""] * 9
            # self.game.current_player = "X"
            self.game.reset_game()
            await self.broadcast(self.game.board_state())
            return True

        return False

    async def broadcast(self, message):
        """Envoie un message à tous les websockets connectés"""
        for ws in list(self.game.connected.keys()):
            try:
                await ws.send(message)
            except:
                # Enlève les connections perdues.
                self.game.connected.pop(ws, None)

    async def close_all_connections(self):
        """Ferme toutes les connections websockets."""
        for ws in list(self.game.connected.keys()):
            try:
                await ws.close()
            except:
                pass
        self.game.connected.clear()
