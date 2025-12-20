import json
from functools import reduce
from typing import NamedTuple
from classes.GameDAO import GameDAO


class Leader(NamedTuple):
    username: str
    points: int


class LeaderboardHelper:

  def __init__(self, file_path = "leaderboard.json"):
      self.file_path = file_path

  def score_game(self, game):
      player, result = game
      return (player, {
          "win": 100,
          "draw": 50,
          "loss": 0
      }[result])

  def accumulate_scores(self, leaderboard, entry):
      player, points = entry
      return {
          **leaderboard,
          player: leaderboard.get(player, 0) + points
      }


  def set_leaderbord_file(self, dao = GameDAO("tictactoe.db")):

      games = dao.get_game_results()

      leaderboard = reduce(
          self.accumulate_scores,          # ✅ reducer (2 args)
          map(self.score_game, games),      # ✅ mapper (1 arg)
          {}
      )

      sorted_board = list(
          map(
              lambda x: Leader(x[0], x[1]),
              sorted(
                  leaderboard.items(),
                  key=lambda x: x[1],
                  reverse=True
              )
          )
      )

      data = [leader._asdict() for leader in sorted_board[:10]]

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
