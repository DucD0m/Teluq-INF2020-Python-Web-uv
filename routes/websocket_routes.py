"""
Routes WebSocket pour le jeu Tic-Tac-Toe.

Ce module définit la route WebSocket principale permettant :
- La connexion des joueurs et spectateurs
- L'échange des coups en temps réel
- La gestion de l'état de la partie
- La détection des victoires, égalités et déconnexions
- La diffusion des mises à jour à tous les clients connectés

Certaines parties du code sont exclues de la couverture de tests
(`# pragma: no cover`) car leur logique est testée indirectement via
les tests unitaires des classes Game et WebsocketHelper.
"""
from classes.WebsocketHelper import WebsocketHelper


def register_websocket_routes(app, game):
    """Enregistre les routes WebSocket liées au jeu Tic-Tac-Toe.

    Cette fonction définit la route `/ws`, utilisée pour gérer les
    connexions WebSocket des joueurs et spectateurs, ainsi que le
    déroulement complet d'une partie.

    Args:
        app (Sanic): Instance de l'application Sanic.
        game (Game): Instance de la classe Game représentant l'état du jeu.
    """

    @app.websocket("/ws")
    async def ws_handler(request, ws):
        """Gestionnaire principal de la connexion WebSocket.

        Ce handler :
        - Assigne un symbole au client: X, O ou S (spectateur)
        - Gère la réception et la validation des coups
        - Met à jour l'état du plateau
        - Détecte les victoires et égalités
        - Enregistre les résultats en base de données
        - Diffuse les mises à jour à tous les clients connectés

        Args:
            request (sanic.request.Request): Requête WebSocket initiale.
            ws (sanic.websocket.WebSocketProtocol): Connexion WebSocket active.
        """
        wsh = WebsocketHelper(game)

        # Attribution du symbole au joueur (X, O ou spectateur)
        player = game.assign_symbol(ws)  # pragma: no cover

        # Association de l'utilisateur connecté au websocket
        user_id = request.cookies.get("id")
        ws.user_id = int(user_id) if user_id else None

        # Envoi du symbole au client
        await ws.send("YOU|" + player)

        # Diffusion de l'état initial du plateau
        await wsh.broadcast(game.board_state())  # pragma: no cover

        try:
            while True:
                # Réception d'un coup depuis le client
                move = await ws.recv()

                # Vérifie si l'autre joueur est toujours connecté
                if await wsh.check_disconnect(ws, player):  # pragma: no cover
                    continue

                # Validation du coup
                cell_id = game.validate_move(player, move)  # pragma: no cover
                if cell_id is None:
                    continue

                # Inscription du coup sur le plateau
                game.board[cell_id] = player

                # Vérification d'une condition gagnante
                winner = game.check_winner(game.board)  # pragma: no cover
                if winner:
                    await wsh.broadcast(game.board_state())  # pragma: no cover
                    await wsh.broadcast("WIN|" + winner)  # pragma: no cover

                    # Enregistrement de la partie
                    game.insert_game(winner)  # pragma: no cover

                    # Fermeture de toutes les connexions
                    await wsh.close_all_connections()  # pragma: no cover

                    # Réinitialisation du jeu
                    game.reset_game()  # pragma: no cover

                    continue

                # Vérification d'une partie nulle
                if game.board_full(game.board):  # pragma: no cover
                    await wsh.broadcast(game.board_state())  # pragma: no cover
                    await wsh.broadcast("DRAW")  # pragma: no cover

                    game.insert_game(0)  # pragma: no cover
                    await wsh.close_all_connections()  # pragma: no cover
                    game.reset_game()  # pragma: no cover
                    continue

                # Changement du joueur actif
                if game.current_player == "X":
                    game.current_player = "O"
                else:
                    game.current_player = "X"

                # Diffusion du nouvel état du plateau
                await wsh.broadcast(game.board_state())  # pragma: no cover

        finally:
            # Nettoyage de la connexion websocket
            game.connected.pop(ws, None)
