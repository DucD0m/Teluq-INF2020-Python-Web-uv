from classes.GameDAO import GameDAO

class Game:

    def __init__(self):
        self.connected = {}  # clé: ws, valeur: player_symbol ("X" ou "O")
        self.board = [""] * 9
        self.current_player = "X"

    def assign_symbol(self, ws):
        if "O" not in self.connected.values():
            player_symbol = "O"
        elif "X" not in self.connected.values():
            player_symbol = "X"
        else:
            player_symbol = "S"  # spectateur

        self.connected[ws] = player_symbol

        return player_symbol

    def validate_move(self, player_symbol, move):
        """Return valid index or None if invalid."""
        # Message doit être un entier
        try:
            idx = int(move)
        except:
            return None

        # Index valide ?
        if idx < 0 or idx > 8:
            return None

        # Spectateurs ne jouent pas
        if player_symbol not in ("X", "O"):
            return None

        # Tour du joueur ?
        if player_symbol != self.current_player:
            return None

        # Case déjà prise ?
        if self.board[idx] != "":
            return None

        return idx

    def check_winner(self, board_state):
        """Retourne 'X' ou 'O' s'il y a un gagnant, ou None."""
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rangs
            (0, 3, 6), (1, 4, 7), (2, 5, 8),   # colonnes
            (0, 4, 8), (2, 4, 6)               # diagonales
        ]
        for a, b, c in wins:
            if board_state[a] != "" and board_state[a] == board_state[b] == board_state[c]:
                return board_state[a]
        return None

    def board_full(self, b):
        return all(cell != "" for cell in b)

    def reset_game(self):
        self.board = [""] * 9
        self.current_player = "X"

    def insert_game(self,winner_symbol):
        dao = GameDAO("tictactoe.db")
        playerX = None
        playerO = None

        for client_ws, symbol in self.connected.items():
            if symbol == "X":
                playerX = client_ws.user_id
            elif symbol == "O":
                playerO = client_ws.user_id

        if winner_symbol == "X":
            winner_uid = playerX
        elif winner_symbol == "O":
            winner_uid = playerO
        else:
            winner_uid = 0 # Partie nulle. Gagnant -> 0.

        # winner_uid = playerX if winner_symbol == "X" else playerO

        dao.insert_game(playerX, playerO, winner_uid)

    def board_state(self):
        """Retourne un chaîne de caractères représentant le jeu ainsi que le joueur actif."""
        return ",".join(self.board) + "|" + self.current_player
