import unittest
from unittest.mock import patch, MagicMock
from classes.Game import Game

## Dépendances
## pip install --user coverage unittest-xml-reporting colorama
## pip install --user coverage-badge
## pip install --user pytest pytest-cov

## Utilisation
## python -m unittest discover -s tests (Raport simple)
## coverage run --rcfile=.coveragerc -m unittest discover -s tests (Test avec rapport de couverture)
## coverage report -m (Afficher rapport de couverture)
## coverage html (Rapport en version page web, htmlcov/index.html pour visualiser)
## coverage xml (Rapport sous format XML, utilisé par GitHub Actions.)
## coverage-badge -o coverage.svg (Pour badge de couverture dans GitHub)


## python -m pytest --cov=classes --cov-report=term-missing (pour utiliser visualisation avec pytest)



class FakeWS:
    def __init__(self, user_id=None):
        self.user_id = user_id

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    ### Tests pour assign_symbol() ###
    def test_assign_symbol_X_then_O(self):
        ws1 = FakeWS()
        ws2 = FakeWS()

        s1 = self.game.assign_symbol(ws1)
        s2 = self.game.assign_symbol(ws2)

        self.assertEqual(s1, "O")
        self.assertEqual(s2, "X")
        self.assertEqual(self.game.connected[ws1], "O")
        self.assertEqual(self.game.connected[ws2], "X")

    def test_assign_symbol_spectator(self):
        ws1 = FakeWS()
        ws2 = FakeWS()
        ws3 = FakeWS()

        self.game.assign_symbol(ws1)
        self.game.assign_symbol(ws2)
        s3 = self.game.assign_symbol(ws3)

        self.assertEqual(s3, "S")

    ### Tests pour validate_move() ###
    def test_validate_move_valid(self):
        idx = self.game.validate_move("X", "4")
        self.assertEqual(idx, 4)

    def test_validate_move_not_integer(self):
        self.assertIsNone(self.game.validate_move("X", "abc"))

    def test_validate_move_out_of_range(self):
        self.assertIsNone(self.game.validate_move("X", 9))
        self.assertIsNone(self.game.validate_move("X", -1))

    def test_validate_move_wrong_player(self):
        self.game.current_player = "O"
        self.assertIsNone(self.game.validate_move("X", 3))

    def test_validate_move_spectator(self):
        self.assertIsNone(self.game.validate_move("S", 3))

    def test_validate_move_cell_taken(self):
        self.game.board[3] = "X"
        self.assertIsNone(self.game.validate_move("X", 3))

    ### Tests pour check_winner() ###
    def test_check_winner_row(self):
        board = ["X","X","X","","","","","",""]
        self.assertEqual(self.game.check_winner(board), "X")

    def test_check_winner_column(self):
        board = ["O","","","O","","","O","",""]
        self.assertEqual(self.game.check_winner(board), "O")

    def test_check_winner_diagonal(self):
        board = ["X","","","","X","","","","X"]
        self.assertEqual(self.game.check_winner(board), "X")

    def test_check_winner_none(self):
        board = ["X","O","X","X","O","O","O","X","X"]
        self.assertIsNone(self.game.check_winner(board))

    ### Tests pour board_full() ###
    def test_board_full_true(self):
        board = ["X"] * 9
        self.assertTrue(self.game.board_full(board))

    def test_board_full_false(self):
        board = ["X",""] * 4 + [""]
        self.assertFalse(self.game.board_full(board))

    ### Tests pour reset_game() ###
    def test_reset_game(self):
        self.game.board = ["X"] * 9
        self.game.current_player = "O"

        self.game.reset_game()

        self.assertEqual(self.game.board, [""] * 9)
        self.assertEqual(self.game.current_player, "X")

    ### Tests pour board_state() ###
    def test_board_state(self):
        self.game.board = ["X","","O","","","","","",""]
        self.game.current_player = "O"

        state = self.game.board_state()
        self.assertEqual(state, "X,,O,,,,,,|O")

    ### Tests pour insert_game() ###
    @patch("classes.Game.GameDAO")
    def test_insert_game_X_wins(self, MockDAO):
        wsX = FakeWS(user_id=1)
        wsO = FakeWS(user_id=2)

        self.game.connected = {
            wsX: "X",
            wsO: "O"
        }

        mock_dao = MockDAO.return_value

        self.game.insert_game("X")

        mock_dao.insert_game.assert_called_once_with(1, 2, 1)

    @patch("classes.Game.GameDAO")
    def test_insert_game_O_wins(self, MockDAO):
        wsX = FakeWS(user_id=1)
        wsO = FakeWS(user_id=2)

        self.game.connected = {
            wsX: "X",
            wsO: "O"
        }

        mock_dao = MockDAO.return_value

        self.game.insert_game("O")

        mock_dao.insert_game.assert_called_once_with(1, 2, 2)

    @patch("classes.Game.GameDAO")
    def test_insert_game_draw(self, MockDAO):
        wsX = FakeWS(user_id=1)
        wsO = FakeWS(user_id=2)

        self.game.connected = {
            wsX: "X",
            wsO: "O"
        }

        mock_dao = MockDAO.return_value

        self.game.insert_game(None)

        mock_dao.insert_game.assert_called_once_with(1, 2, 0)
