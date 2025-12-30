from classes.WebsocketHelper import WebsocketHelper

# # pragma: no cover -> On ne calcule pas certaines parties du code dans les tests de couverture.
# Les fonctions sont testées dans les tests des classes Game et WebsocketHelper.

def register_websocket_routes(app, game):

  @app.websocket("/ws")
  async def ws_handler(request, ws):

      wsh = WebsocketHelper(game)

      player = game.assign_symbol(ws)  # pragma: no cover

      user_id = request.cookies.get("id")
      ws.user_id = int(user_id) if user_id else None

      await ws.send("YOU|" + player)
      await wsh.broadcast(game.board_state())  # pragma: no cover


      try:
          while True:
              move = await ws.recv()

              # Vérifie si l'autre joueur est toujours connecté
              if await wsh.check_disconnect(ws, player):  # pragma: no cover
                  continue

              # Validation du coup
              cell_id = game.validate_move(player, move)  # pragma: no cover
              if cell_id is None:
                  continue

              # Inscription du coup.
              game.board[cell_id] = player

              # Vérifie si une condition gagnante est présente.
              winner = game.check_winner(game.board)  # pragma: no cover
              if winner:
                  await wsh.broadcast(game.board_state())  # pragma: no cover
                  await wsh.broadcast("WIN|" + winner)  # pragma: no cover

                  game.insert_game(winner)  # pragma: no cover

                  # Ferme toutes les connections.
                  await wsh.close_all_connections()  # pragma: no cover

                  # Réinitialisation de la partie.
                  game.reset_game()  # pragma: no cover

                  continue

              # Vérifie si la partie est nulle.
              if game.board_full(game.board):  # pragma: no cover
                  await wsh.broadcast(game.board_state())  # pragma: no cover
                  await wsh.broadcast("DRAW")  # pragma: no cover

                  game.insert_game(0)  # pragma: no cover
                  await wsh.close_all_connections()  # pragma: no cover
                  game.reset_game()  # pragma: no cover
                  continue

              # Changement du premier joueur à jouer pour la prochaine partie.
              game.current_player = "O" if game.current_player == "X" else "X"
              await wsh.broadcast(game.board_state())  # pragma: no cover


      finally:
          # Nettoyage des connections.
          game.connected.pop(ws, None)
