import json
from functools import reduce
from collections import namedtuple
from classes.GameDAO import GameDAO


class LeaderboardHelper:

  def __init__(self, file_path = "leaderboard.json"):
      self.file_path = file_path

  def score_game(self, game):
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
      player, points = scored_game
      current_score = leaderboard.get(player, 0)
      new_leaderboard = leaderboard.copy()
      new_leaderboard[player] = current_score + points
      return new_leaderboard

  def set_leaderboard_file(self, dao = GameDAO("tictactoe.db")):
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
          key = lambda item: item[1],
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
      message = "Le tableau des meneurs n'est pas disponible en ce moment."
      try:
          with open(self.file_path, 'r') as f:
              data = json.load(f)
              return data
      except:
          return message
