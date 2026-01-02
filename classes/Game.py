"""Gestion de la logique d’une partie de Tic-Tac-Toe.

Ce module définit la classe `Game`, responsable de la logique métier
du jeu Tic-Tac-Toe. Il gère l’état du plateau, les joueurs connectés,
la validation des coups, la détection des conditions de victoire ou
d’égalité, ainsi que l’enregistrement des résultats en base de données.

Le module est conçu pour être utilisé conjointement avec des connexions
WebSocket et une couche d’accès aux données via `GameDAO`.
"""
from classes.GameDAO import GameDAO


class Game:
    """Représente l’état et la logique d’une partie de Tic-Tac-Toe.

    Cette classe gère :
    - les joueurs connectés via WebSocket,
    - l’état du plateau de jeu,
    - la validation des coups,
    - la détection des conditions de victoire ou d’égalité,
    - la persistance des résultats en base de données.
    """

    def __init__(self):
        """Initialise une nouvelle partie.

        Args:
            connected (dict): Dictionnaire associant un WebSocket à
                un symbole de joueur ("X", "O" ou "S" pour spectateur).
            board (list[str]): Liste représentant les 9 cases du
                plateau de jeu.
            current_player (str): Symbole du joueur dont c’est le tour.
        """
        self.connected = {}  # clé: ws, valeur: player ("X" ou "O")
        self.board = [""] * 9
        self.current_player = "X"

    def assign_symbol(self, ws):
        """Attribue un symbole à un nouveau joueur connecté.

        Le premier joueur reçoit "O", le second "X".
        Les connexions supplémentaires sont considérées comme des
        spectateurs ("S").

        Args:
            ws: WebSocket du client connecté.

        Returns:
            str: Symbole attribué au client ("X", "O" ou "S").
        """
        if "O" not in self.connected.values():
            player = "O"
        elif "X" not in self.connected.values():
            player = "X"
        else:
            player = "S"  # spectateur

        self.connected[ws] = player

        return player

    def validate_move(self, player, move):
        """Valide un coup proposé par un joueur.

        Vérifie que :
        - le coup est un entier valide,
        - la cellule est comprise entre 0 et 8,
        - le joueur n’est pas un spectateur,
        - c’est bien le tour du joueur,
        - la case ciblée est libre.

        Args:
            player (str): Symbole du joueur ("X" ou "O").
            move (str): Coup envoyé par le client.

        Returns:
            int | None: Index de la cellule valide, ou None si le coup
            est invalide.
        """
        try:
            cell = int(move)
        except (ValueError, TypeError):
            return None

        if cell < 0 or cell > 8:
            return None

        if player not in ("X", "O"):
            return None

        if player != self.current_player:
            return None

        if self.board[cell] != "":
            return None

        return cell

    def check_winner(self, board_state):
        """Détermine s’il existe un gagnant.

        Analyse toutes les combinaisons gagnantes possibles
        (lignes, colonnes et diagonales).

        Args:
            board_state (list[str]): État actuel du plateau.

        Returns:
            str | None: Symbole du gagnant ("X" ou "O") s’il existe,
            sinon None.
        """
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rangs
            (0, 3, 6), (1, 4, 7), (2, 5, 8),   # colonnes
            (0, 4, 8), (2, 4, 6)               # diagonales
        ]
        for a, b, c in wins:
            if (
                board_state[a] != ""
                and board_state[a] == board_state[b]
                and board_state[b] == board_state[c]
            ):
                return board_state[a]

        return None

    def board_full(self, board):
        """Indique si le plateau est entièrement rempli.

        Args:
            board (list[str]): Plateau à vérifier.

        Returns:
            bool: True si toutes les cases sont occupées, sinon False.
        """
        return all(cell != "" for cell in board)

    def reset_game(self):
        """Réinitialise la partie.

        Vide le plateau de jeu et redonne le premier tour
        au joueur "X".
        """
        self.board = [""] * 9
        self.current_player = "X"

    def insert_game(self, winner):
        """Enregistre le résultat de la partie en base de données.

        Associe les identifiants des joueurs "X" et "O" à partir
        des connexions actives et détermine l’identifiant du gagnant.

        Args:
            winner (str | None): Symbole du gagnant ("X", "O") ou None
                en cas de partie nulle.
        """
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
            winner_id = 0  # Partie nulle. Gagnant -> 0.

        dao.insert_game(player_x, player_o, winner_id)

    def board_state(self):
        """Retourne l’état du jeu sous forme sérialisée.

        Le format retourné est :
        - les 9 cases séparées par des virgules,
        - suivies du joueur courant séparé par un "|".

        Returns:
            str: Représentation textuelle du plateau et du joueur actif.
        """
        return ",".join(self.board) + "|" + self.current_player
