import sqlite3

class GameDAO:

    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Assure que les tables requises par la classe existent avant l'exécution des fonctions."""
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

    def insert_game(self, playerX: int, playerO: int, winner: int):
        """Insère une partie dans la base de données. 0 indique une partie nulle."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (playerX, playerO, winner)
                VALUES (:x, :o, :w)
            """, {"x": playerX, "o": playerO, "w": winner})
            return cursor.lastrowid

    def get_game_results(self):
        """Retourne la liste des parties par utilisateurs avec leur résultat propre."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row # Permet l'accès aux colonnes par leur nom.
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
