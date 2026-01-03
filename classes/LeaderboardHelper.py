"""
Gestion du tableau des meneurs (leaderboard) du jeu Tic-Tac-Toe.

Ce module fournit la classe LeaderboardHelper, responsable du calcul
des scores des joueurs à partir des résultats stockés en base de
données, du tri des meilleurs joueurs et de la persistance du
classement dans un fichier JSON.
"""
import json
from functools import reduce
from collections import namedtuple
from classes.GameDAO import GameDAO


class LeaderboardHelper:
    """Classe utilitaire pour le calcul et la gestion du leaderboard.

    Cette classe :
    - transforme les résultats des parties en scores,
    - cumule les points par joueur,
    - génère le top 10 des joueurs,
    - sauvegarde et charge le leaderboard depuis un fichier JSON.
    """

    def __init__(self, file_path="leaderboard.json"):
        """Initialise le helper du leaderboard.

        Args:
            file_path (str): Chemin du fichier JSON dans lequel le
                leaderboard est sauvegardé.
        """
        self.file_path = file_path

    def score_game(self, game):
        """Convertit un résultat de partie en points.

        Args:
            game (tuple[str, str]): Tuple contenant le nom du joueur
                et le résultat de la partie ("win", "draw" ou "loss").

        Returns:
            tuple[str, int]: Tuple contenant le nom du joueur et le
            nombre de points attribués pour cette partie.
        """
        player, result = game

        match result:
            case "win":
                score = 100
            case "draw":
                score = 50
            case "loss":
                score = 0
            case _:
                score = 0

        return player, score

    def add_points(self, leaderboard, scored_game):
        """Ajoute des points au score total d'un joueur.

        Cette méthode retourne un nouveau dictionnaire afin d'éviter
        toute modification directe du leaderboard existant.

        Args:
            leaderboard (dict[str, int]): Dictionnaire des scores
                actuels par joueur.
            scored_game (tuple[str, int]): Tuple contenant le nom du
                joueur et les points à ajouter.

        Returns:
            dict[str, int]: Nouveau leaderboard mis à jour.
        """
        player, points = scored_game
        current_score = leaderboard.get(player, 0)
        new_leaderboard = leaderboard.copy()
        new_leaderboard[player] = current_score + points
        return new_leaderboard

    def set_leaderboard_file(self, dao = GameDAO("tictactoe.db")):
        """Calcule et sauvegarde le leaderboard dans un fichier JSON.

        Cette méthode :
        - récupère les résultats des parties depuis la base de données,
        - calcule les scores cumulés par joueur,
        - sélectionne les 10 meilleurs joueurs,
        - écrit le résultat dans un fichier JSON.

        Args:
            dao (GameDAO): Objet d'accès aux données permettant de
                récupérer les résultats des parties.
        """
        data = []
        games = dao.get_game_results()
        Leader = namedtuple("Leader", ["username", "points"])

        leaderboard = reduce(
            self.add_points,
            map(self.score_game, games),
            {}
        )

        sorted_leaderboard = sorted(
            leaderboard.items(),
            key=lambda item: item[1],
            reverse=True
        )

        named_leaderboard = list(
            map(
                lambda item: Leader(item[0], item[1]),
                sorted_leaderboard[:10]
            )
        )

        for leader in named_leaderboard:
            leader_asdict = leader._asdict()
            data.append(leader_asdict)

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_leaderboard_file(self):
        """Charge le leaderboard depuis le fichier JSON.

        Returns:
            list[dict] | str: Liste des joueurs du leaderboard si le
            fichier est disponible, sinon un message d'erreur indiquant
            que le classement est indisponible.
        """
        message = "Le tableau des meneurs n'est pas disponible en ce moment."

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return data

        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            return message
