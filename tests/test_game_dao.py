import sqlite3
import unittest
import tempfile
import os
from classes.GameDAO import GameDAO

class TestGameDAO(unittest.TestCase):
    def setUp(self):
        # Fichier temporaire pour la base
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.db_file.name
        self.db_file.close()  # On ferme le fichier, SQLite l’ouvrira

        # Crée la table users
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        """)
        cur.executemany(
            "INSERT INTO users (username) VALUES (?)",
            [("Alice",), ("Bob",), ("Charlie",)]
        )
        conn.commit()
        conn.close()

        # Instancie GameDAO, qui créera la table games
        self.dao = GameDAO(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)  # supprime le fichier temporaire

    def test_insert_game(self):
        game_id = self.dao.insert_game(1, 2, 1)
        self.assertIsInstance(game_id, int)

    def test_get_leaderboard_empty(self):
        leaderboard = self.dao.get_leaderboard()
        self.assertIsInstance(leaderboard, list)
        self.assertEqual(len(leaderboard), 0)

    def test_get_leaderboard_with_games(self):
        self.dao.insert_game(1, 2, 1)
        self.dao.insert_game(2, 3, 2)
        self.dao.insert_game(1, 3, 1)

        leaderboard = self.dao.get_leaderboard()
        self.assertEqual(leaderboard[0]["username"], "Alice")
        self.assertEqual(leaderboard[0]["wins"], 2)
