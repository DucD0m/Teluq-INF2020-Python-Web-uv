import sqlite3


class UserDAO:

    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Assure que la table users existe avant les appels de méthodes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)

    def insert_user(self, username, password):
        """ Insertion d'un utilisateur. Retourne le id en cas de réussite, 0 si le nom d'utilisateur existe déjà."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES (:username, :password)
                """, {"username": username, "password": password})
                return cursor.lastrowid

            except sqlite3.IntegrityError: # Si le nom d'utilisateur existe déjà.
                return 0

    def get_user(self, username, password):
        """Retourne le id et le username ou None."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Permet l'accès aux colonnes comme un dictionnaire.
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username
                FROM users
                WHERE username = :username
                AND password = :password
                LIMIT 1
            """, {"username": username, "password": password})
            return cursor.fetchone()
