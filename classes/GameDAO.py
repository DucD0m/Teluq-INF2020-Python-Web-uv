"""
Accès aux données pour l'application Tic-Tac-Toe.

Ce module définit la classe GameDAO, responsable de la gestion
des interactions avec la base de données SQLite, incluant la
création du schéma, l'insertion des parties et la récupération
des résultats des joueurs.
"""
import sqlite3


class GameDAO:
    """Objet d'accès aux données (DAO) pour les parties et utilisateurs.

    Cette classe encapsule toutes les opérations liées à la base
    de données SQLite : création des tables, insertion des parties
    et récupération des résultats pour le calcul du classement.
    """

    def __init__(self, db_path):
        """Initialise l'accès à la base de données.

        Vérifie que le schéma requis (tables `games` et `users`)
        existe et le crée si nécessaire.

        Args:
            db_path (str): Chemin vers le fichier de base de données SQLite.
        """
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Crée les tables requises si elles n'existent pas.

        Tables créées :
        - games : stocke les parties jouées
        - users : stocke les utilisateurs enregistrés

        Cette méthode est appelée automatiquement lors de
        l'initialisation de l'objet GameDAO.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playerX INTEGER NOT NULL,
                    playerO INTEGER NOT NULL,
                    winner INTEGER NOT NULL,
                    gametime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)

    def insert_game(self, player_x, player_o, winner):
        """Insère une nouvelle partie dans la base de données.

        Une valeur de `winner` égale à 0 indique une partie nulle.

        Args:
            player_x (int): Identifiant de l'utilisateur jouant avec X.
            player_o (int): Identifiant de l'utilisateur jouant avec O.
            winner (int): Identifiant du gagnant ou 0 en cas de match nul.

        Returns:
            int: Identifiant (ID) de la partie nouvellement insérée.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (playerX, playerO, winner)
                VALUES (:x, :o, :w)
            """, {"x": player_x, "o": player_o, "w": winner})
            return cursor.lastrowid

    def get_game_results(self):
        """Retourne les résultats des parties par joueur.

        Chaque partie génère deux entrées :
        - une pour le joueur X
        - une pour le joueur O

        Le champ `result` contient :
        - "win"  : victoire du joueur
        - "draw" : partie nulle
        - "loss" : défaite du joueur

        Returns:
            list[tuple[str, str]]: Liste de tuples (username, result),
            triée par nom d'utilisateur.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    users.username,
                    CASE
                        WHEN games.winner = games.playerX THEN 'win'
                        WHEN games.winner = 0 THEN 'draw'
                        ELSE 'loss'
                    END AS result
                FROM games
                JOIN users ON users.id = games.playerX

                UNION ALL

                SELECT
                    users.username,
                    CASE
                        WHEN games.winner = games.playerO THEN 'win'
                        WHEN games.winner = 0 THEN 'draw'
                        ELSE 'loss'
                    END AS result
                FROM games
                JOIN users ON users.id = games.playerO

                ORDER BY username
            """)
            return cursor.fetchall()
