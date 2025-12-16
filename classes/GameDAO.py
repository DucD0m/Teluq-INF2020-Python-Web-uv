import sqlite3
import json

class GameDAO:

    def __init__(self, db_path, file_path = "leaderboard.json"):
        self.db_path = db_path
        self.file_path = file_path
        self._ensure_schema()

    def _ensure_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playerX INTEGER NOT NULL,
                    playerO INTEGER NOT NULL,
                    winner INTEGER NOT NULL,
                    gametime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def insert_game(self, playerX: int, playerO: int, winner: int):
        """Insert the game. winner=0 means a draw."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO games (playerX, playerO, winner)
                VALUES (:x, :o, :w)
            """, {"x": playerX, "o": playerO, "w": winner})
            return cur.lastrowid

    def get_leaderboard(self):
        """Returns the top 10 users with the most wins."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    users.username,
                    COUNT(games.winner) AS wins
                FROM games
                JOIN users ON users.id = games.winner
                GROUP BY games.winner
                ORDER BY wins DESC
                LIMIT 10;
            """)
            return cur.fetchall()

    def set_leaderbord_file(self):
        leaderboard = self.get_leaderboard()
        data = [dict(row) for row in leaderboard]

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_leaderboard_file(self):
        message = "Le tableau des meneurs n'est pas disponible en ce moment."
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except:
            return message
