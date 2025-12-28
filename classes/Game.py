from classes.GameDAO import GameDAO


class Game:

    def __init__(self):
        self.connected = {}  # clé: ws, valeur: player ("X" ou "O")
        self.board = [""] * 9
        self.current_player = "X"

    def assign_symbol(self, ws):
        if "O" not in self.connected.values():
            player = "O"
        elif "X" not in self.connected.values():
            player = "X"
        else:
            player = "S"  # spectateur

        self.connected[ws] = player

        return player

    def validate_move(self, player, move):
        """Retourne l'index d'une cellule ou None."""
        # Message doit être un entier
        try:
            cell = int(move)
        except:
            return None

        # Cellule valide
        if cell < 0 or cell > 8:
            return None

        # Spectateurs ne jouent pas
        if player not in ("X", "O"):
            return None

        # Tour du joueur
        if player != self.current_player:
            return None

        # Case déjà prise
        if self.board[cell] != "":
            return None

        return cell

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

    def board_full(self, board):
        return all(cell != "" for cell in board)

    def reset_game(self):
        self.board = [""] * 9
        self.current_player = "X"

    def insert_game(self, winner):
        dao = GameDAO("tictactoe.db")
        player_x = None
        player_o = None

        for client_ws, symbol in self.connected.items():
            if symbol == "X":
                player_x = client_ws.user_id
            elif symbol == "O":
                player_o = client_ws.user_id

        if winner == "X":
            winner_id = player_x
        elif winner == "O":
            winner_id = player_o
        else:
            winner_id = 0 # Partie nulle. Gagnant -> 0.

        dao.insert_game(player_x, player_o, winner_id)

    def board_state(self):
        """Retourne un chaîne de caractères représentant le jeu ainsi que le joueur actif."""
        return ",".join(self.board) + "|" + self.current_player
