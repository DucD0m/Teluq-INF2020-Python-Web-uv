"""
Accès aux données pour la gestion des utilisateurs.

Ce module définit la classe UserDAO, responsable des opérations
liées aux utilisateurs dans la base de données SQLite, incluant
la création du schéma, l'insertion et l'authentification.
"""
import sqlite3


class UserDAO:
    """Objet d'accès aux données (DAO) pour les utilisateurs.

    Cette classe encapsule les opérations de persistance et de
    récupération des utilisateurs dans la base de données.
    """

    def __init__(self, db_path):
        """Initialise l'accès à la base de données utilisateur.

        Vérifie que la table `users` existe et la crée si nécessaire.

        Args:
            db_path (str): Chemin vers le fichier de base de données SQLite.
        """
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self):
        """Gére la connexion à la base de données.

        Cette méthode effectue la gestion des erreurs.
        """
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Erreur de connexion sqlite3 : {e}")
            print(f"Emplacement de la base de données : {self.db_path}")
            raise

    def _ensure_schema(self):
        """Crée la table `users` si elle n'existe pas.

        Cette méthode est appelée automatiquement lors de
        l'initialisation de l'objet UserDAO.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)

    def insert_user(self, username, password):
        """Insère un nouvel utilisateur dans la base de données.

        Si le nom d'utilisateur existe déjà, l'insertion échoue
        silencieusement.

        Args:
            username (str): Nom d'utilisateur unique.
            password (str): Mot de passe associé à l'utilisateur.

        Returns:
            int: Identifiant (ID) de l'utilisateur nouvellement créé
            en cas de succès, ou 0 si le nom d'utilisateur existe déjà.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES (:username, :password)
                """, {"username": username, "password": password})
                return cursor.lastrowid

            # Si le nom d'utilisateur existe déjà.
            except sqlite3.IntegrityError:
                return 0

    def get_user(self, username, password):
        """Récupère un utilisateur à partir de ses identifiants.

        Cette méthode est généralement utilisée pour l'authentification.

        Args:
            username (str): Nom d'utilisateur.
            password (str): Mot de passe associé.

        Returns:
            sqlite3.Row | None: Ligne contenant `id` et `username`
            si l'utilisateur est trouvé, sinon None.
        """
        with self._connect() as conn:
            # Permet l'accès aux colonnes comme un dictionnaire.
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username
                FROM users
                WHERE username = :username
                AND password = :password
                LIMIT 1
            """, {"username": username, "password": password})
            return cursor.fetchone()
