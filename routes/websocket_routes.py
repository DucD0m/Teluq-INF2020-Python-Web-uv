from classes.WebsocketHelper import WebsocketHelper

def register_websocket_routes(app, game):

  @app.websocket("/ws")
  async def ws_handler(request, ws):

      wsh = WebsocketHelper(game)

      player_symbol = game.assign_symbol(ws)

      user_id = request.cookies.get("id")
      ws.user_id = int(user_id) if user_id else None

      await ws.send("YOU|" + player_symbol)
      await wsh.broadcast(game.board_state())


      try:
          while True:
              move = await ws.recv()

              # On ne calcule pas cette partie du code dans les tests de couverture. Les fonctions sont testées
              # dans les tests des classes Game et WebsocketHelper.

              # pragma: no cover start

              # Vérifie si l'autre joueur est toujours connecté
              if await wsh.check_disconnect(ws, player_symbol):
                  continue

              # Validation du coup
              idx = game.validate_move(player_symbol, move)
              if idx is None:
                  continue

              # Inscription du coup.
              game.board[idx] = player_symbol

              # Vérifie si une condition gagnante est présente.
              winner_symbol = game.check_winner(game.board)
              if winner_symbol:
                  await wsh.broadcast(game.board_state())
                  await wsh.broadcast("WIN|" + winner_symbol)

                  game.insert_game(winner_symbol)

                  # Ferme toutes les connections.
                  await wsh.close_all_connections()

                  # Réinitialisation de la partie.
                  game.reset_game()

                  continue

              # Vérifie si la partie est nulle.
              if game.board_full(game.board):
                  await wsh.broadcast(game.board_state())
                  await wsh.broadcast("DRAW")

                  game.insert_game(0)
                  await wsh.close_all_connections()
                  game.reset_game()
                  continue

              # Changement du premier joueur à jouer pour la prochaine partie.
              game.current_player = "O" if game.current_player == "X" else "X"
              await wsh.broadcast(game.board_state())
              # pragma: no cover stop

      finally:
          # Nettoyage des connections.
          try:
              game.connected.pop(ws, None)
          except ValueError:
              pass
