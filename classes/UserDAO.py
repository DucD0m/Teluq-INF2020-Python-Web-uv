import sqlite3

class UserDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Create the users table if it does not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)

    def insert_user(self, username, password):
        """ Insertion d'un utilisateur. Retourne le id en cas de réussite, 0 si le nom d'utilisateur existe déjà"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO users (username, password)
                    VALUES (:username, :password)
                """, {"username": username, "password": password})
                return cur.lastrowid

            except sqlite3.IntegrityError:
                return 0

    def get_user(self, username, password):
        """ Récupération d'un utilisateur avec son mot de passe """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT id, username
                FROM users
                WHERE username = :username
                AND password = :password
                LIMIT 1
            """, {"username": username, "password": password})
            row = cur.fetchone()
            if row:
                return {"id": row["id"], "username": row["username"]}
            return None
