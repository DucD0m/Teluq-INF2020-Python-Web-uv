import unittest
import tempfile
import os
from classes.UserDAO import UserDAO

class TestUserDAO(unittest.TestCase):
    def setUp(self):
        # Crée un fichier temporaire pour la base de données
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.db_file.name
        self.db_file.close()

        # Instancie UserDAO, qui crée la table users
        self.dao = UserDAO(self.db_path)

    def tearDown(self):
        # Supprime le fichier temporaire après les tests
        os.unlink(self.db_path)

    def test_insert_user_success(self):
        """Insertion réussie retourne un id entier"""
        user_id = self.dao.insert_user("Alice", "password123")
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)

    def test_insert_user_duplicate(self):
        """Tentative d'insertion d'un doublon retourne 0"""
        user_id1 = self.dao.insert_user("Bob", "secret")
        self.assertGreater(user_id1, 0)

        user_id2 = self.dao.insert_user("Bob", "secret")
        self.assertEqual(user_id2, 0)

    def test_get_user_success(self):
        """Récupération correcte d'un utilisateur existant"""
        uid = self.dao.insert_user("Charlie", "mypassword")
        user = self.dao.get_user("Charlie", "mypassword")
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], uid)
        self.assertEqual(user["username"], "Charlie")

    def test_get_user_wrong_password(self):
        """Mot de passe incorrect retourne None"""
        self.dao.insert_user("Dave", "pass1")
        user = self.dao.get_user("Dave", "wrongpass")
        self.assertIsNone(user)

    def test_get_user_nonexistent(self):
        """Utilisateur inexistant retourne None"""
        user = self.dao.get_user("NonExistent", "nopass")
        self.assertIsNone(user)

    def test_multiple_users(self):
        """Insertion et récupération de plusieurs utilisateurs"""
        users = [("Eve", "123"), ("Frank", "abc"), ("Grace", "xyz")]
        ids = []
        for username, pwd in users:
            uid = self.dao.insert_user(username, pwd)
            ids.append(uid)
            self.assertGreater(uid, 0)

        # Vérifie que chaque utilisateur peut se connecter
        for (username, pwd), uid in zip(users, ids):
            user = self.dao.get_user(username, pwd)
            self.assertEqual(user["id"], uid)
            self.assertEqual(user["username"], username)
