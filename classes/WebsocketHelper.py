"""
Gestion des connexions WebSocket pour le jeu Tic-Tac-Toe.

Ce module fournit des utilitaires pour gérer les connexions WebSocket
associées à une partie en cours. Il permet notamment :
- de détecter la déconnexion d'un joueur,
- de réinitialiser la partie en cas de déconnexion,
- de diffuser des messages à l'ensemble des joueurs connectés,
- de fermer proprement toutes les connexions actives.

Ce module est conçu pour être utilisé avec une instance de jeu
maintenant l'état de la partie et le registre des connexions WebSocket.
"""


class WebsocketHelper:
    """Classe utilitaire pour la gestion des connexions WebSocket.

    Cette classe centralise les opérations liées aux WebSockets
    d'une partie : détection des déconnexions, diffusion des messages
    et fermeture propre des connexions actives.
    """

    def __init__(self, game):
        """Initialise le helper WebSocket.

        Args:
            game: Instance du jeu associée, contenant l'état de la partie
                ainsi que les connexions WebSocket actives.
        """
        self.game = game

    async def check_disconnect(self, ws, player):
        """Vérifie si l'autre joueur est déconnecté.

        Si l'autre joueur n'est plus connecté :
        - un message d'information est envoyé au joueur courant,
        - la partie est réinitialisée,
        - l'état initial du plateau est diffusé à tous les joueurs.

        Args:
            ws: WebSocket du joueur courant.
            player (str): Symbole du joueur courant ("X" ou "O").

        Returns:
            bool: True si une déconnexion de l'autre joueur a été détectée
            et que la partie a été réinitialisée, sinon False.
        """
        if player not in ("X", "O"):
            return False

        other_player = "O" if player == "X" else "X"

        if other_player not in self.game.connected.values():
            try:
                await ws.send(
                    "DISC|La connexion avec l'autre joueur a été perdue. "
                    + "La partie sera réinitialisée."
                )
            except (Exception, AttributeError):
                self.game.connected.pop(ws, None)

            self.game.reset_game()
            await self.broadcast(self.game.board_state())
            return True

        return False

    async def broadcast(self, message):
        """Diffuse un message à toutes les connexions WebSocket actives.

        Les connexions invalides ou fermées sont automatiquement
        supprimées de la liste des connexions actives.

        Args:
            message (str): Message à envoyer à tous les joueurs connectés.
        """
        for ws in list(self.game.connected.keys()):
            try:
                await ws.send(message)
            except (Exception, AttributeError):
                self.game.connected.pop(ws, None)

    async def close_all_connections(self):
        """Ferme toutes les connexions WebSocket actives.

        Cette méthode ferme chaque connexion proprement, puis
        supprime toutes les entrées du dictionnaire des connexions.
        Elle est généralement utilisée lors de l'arrêt ou de la
        réinitialisation complète du serveur.
        """
        for ws in list(self.game.connected.keys()):
            try:
                await ws.close()
            except (Exception, AttributeError):
                pass
            finally:
                self.game.connected.pop(ws, None)
