# from models.piece.pieces_info import PIECE_VALUES, PROM_PIECE_VALUES
# from models.piece.piece import Piece
# from models.game.board import Board
# from models.game.player import Player
# from models.game.action_manager import ActionManager

# class Simulator:
#     """
#     Simulator class for evaluating and simulating game actions.
#     """
#     @staticmethod
#     def simulate_action(player: Player, board: Board, action: dict) -> float:
#         """
#         Simulates the specified action and returns the evaluation score.

#         Args:
#             player (Player): The player performing the action
#             board (Board): The current board state
#             action (dict): A dictionary containing action details

#         Returns:
#             float: Evaluation score after the action is performed
#         """
#         player = player.copy()
#         board = board.copy()

#         ActionManager.action(
#             player,
#             board,
#             action['target_piece_id'],
#             action['promote'],
#             action['action_type'],
#             action['x'],
#             action['y'],
#         )

#         # Evaluate the game state after performing the action
#         return Simulator.evaluate_state(player.team, board.pieces.values())

#     @staticmethod
#     def evaluate_state(team: str, pieces: list[Piece]) -> float:
#         """
#         Evaluates the current game state and returns a score.

#         Args:
#             team (str): The team to evaluate the score for ("white" or "black")
#             pieces (list[Piece]): List of pieces on the board

#         Returns:
#             float: The evaluation score
#         """
#         score = 0
#         for piece in pieces:
#             piece_value = (PROM_PIECE_VALUES[piece.name] if piece.is_promoted 
#                            else PIECE_VALUES[piece.name])
#             score += piece_value if piece.team == team else -piece_value
#         return score

#     @staticmethod
#     def generate_possible_actions(player: Player, board: Board) -> list[dict]:
#         """
#         Generates all possible actions for the current player.

#         Args:
#             player (Player): The current player
#             board (Board): The current board state

#         Returns:
#             list[dict]: A list of possible actions
#         """
#         actions = []
#         for piece in board.pieces.values():
#             if piece.team != player.team:
#                 continue

#             for move, _ in piece.get_legal_moves(board.pieces):
#                 actions.append(Simulator._create_action(piece.piece_id, move, False, "move"))
#                 if piece.can_promote(move[1]):
#                     actions.append(Simulator._create_action(piece.piece_id, move, True, "move"))

#         return actions

#     @staticmethod
#     def _create_action(piece_id: int, move: tuple[int, int], promote: bool, action_type: str) -> dict:
#         """
#         Creates an action dictionary.

#         Args:
#             piece_id (int): The piece's ID
#             move (tuple[int, int]): The target move coordinates
#             promote (bool): Whether the promotion occurs
#             action_type (str): The type of action ("move" or "place")

#         Returns:
#             dict: A dictionary representing the action
#         """
#         return {
#             "target_piece_id": piece_id,
#             "promote": promote,
#             "action_type": action_type,
#             "x": move[0],
#             "y": move[1],
#         }
