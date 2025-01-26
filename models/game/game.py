from models.game.board import Board
from models.game.player import Player
from models.send_data_manager import SendDataManager
from models.game.hash_board import hash_board
from models.game.action_manager import ActionManager  # Import ActionManager
import copy

class Game:
    REPEAT_LIMIT = 4

    def __init__(self, black: Player, white: Player, board: Board):
        self.__black = black
        self.__white = white
        self.__board = board

        self.history = []
        self.board_count = {}
        self.step = 1
        self.last_move = None  # Last move recorded as a dictionary

    @property
    def black(self):
        return self.__black
    
    @property
    def white(self):
        return self.__white
    
    @property
    def board(self):
        return self.__board

    @property
    def current_player(self):
        return self.white if self.step % 2 == 1 else self.black

    def add_history(self):
        board_hash = hash_board(
            self.board.pieces, 
            self.board.size, 
            self.black.captured_pieces, 
            self.white.captured_pieces
        )
        self.history.append(board_hash)
        self.board_count[board_hash] = self.board_count.get(board_hash, 0) + 1

    def check_repetition(self):
        return max(self.board_count.values(), default=0) >= self.REPEAT_LIMIT

    def next_turn(self):
        self.add_history()
        self.step += 1

        # if self.check_repetition():
        #     self.game_set()
        # else:
        #     self.step += 1

    def game_set(self):
        print("The game is a draw due to repetition.")

    def is_game_over(self):
        # TODO: Implement the logic to determine if the game is over
        return False

    def to_dict(self):
        return {
            "black": self.black.to_dict(),
            "white": self.white.to_dict(),
            "board": self.board.to_dict(),
            "step": self.step,
            "last_move": self.last_move,
        }

    @staticmethod
    def from_dict(data):
        black = Player.from_dict(data["black"])
        white = Player.from_dict(data["white"])
        board = Board.from_dict(data["board"])
        game = Game(black=black, white=white, board=board)
        game.step = data["step"]
        game.last_move = data["last_move"]
        return game
    
    def get_game_data_dict(self):
        board_settings = {
            "type": self.board.board_type,
            "size": self.board.size,
            "blackBoard": self.board.black_board,
            "whiteBoard": self.board.white_board
        }

        game_state = {
            "pieces": self.board.pieces or {},
            "board_settings": board_settings,
            "board_size": board_settings["size"],
            "black_captured_pieces": self.black.captured_pieces or [],
            "white_captured_pieces": self.white.captured_pieces or [],
            "current_team": self.current_player.team,
            "step": self.step,
            "last_move": self.last_move,
            "white_checked": False,  # Placeholder for check status
            "black_checked": False,  # Placeholder for check status
            "game_result": None,  # Game result (draw, win, etc.)
            "error": None  # Error messages if any
        }

        return SendDataManager.create_game_data_dict(game_state)

    def perform_action(self, target_piece_id, promote, action_type, x, y):
        # Use ActionManager to perform the action
        last_move = ActionManager.action(self.current_player, self.board, target_piece_id, promote, action_type, x, y)

        # Update the last move and check for repetition
        self.last_move = last_move
        self.next_turn()  # Move to the next turn after an action is performed
