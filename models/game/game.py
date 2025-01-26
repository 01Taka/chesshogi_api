from models.game.board import Board
from server.models.game.player import Player
from models.piece.piece import Piece
from models.piece.chess_pieces import ChessKing, ChessRook, ChessPawn
from models.send_data_manager import SendDataManager
from server.models.game.hash_board import hash_board
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
        self.last_move = None  # 最後の移動や配置アクションを記録する辞書
    
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

    def action(self, target_piece_id, promote, action_type, x, y):
        if action_type == "move":
            piece: Piece = self.board.get_piece_by_id(target_piece_id)
        elif action_type == "place":
            piece: Piece = self.current_player.get_captured_piece_by_id(target_piece_id)
        else:
            print("Action type error")
            raise ValueError("ActionTypeに一致する行動がありません")
        
        if not piece:
            print("ID error")
            raise ValueError("IDに一致する駒がありません")
        
        if piece.team != self.current_player.team:
            print("Team error")
            raise ValueError("プレイヤーと駒のチームが一致しません")

        if (piece.position and action_type == "place") or (not piece.position and action_type == "move"):
            print("Action error")
            raise ValueError("駒の状態と行動が一致しません")

        if action_type == "move":
            prev_position_y = piece.position[1]
            self.move_piece(piece, (x, y))
            if promote:
                piece.set_promote(True, prev_position_y)
        elif action_type == "place":
            self.place_piece(piece, (x, y))

        # 最後のアクションを記録
        self.last_move = {
            "action_type": action_type,
            "piece_id": target_piece_id,
            "piece_name": piece.name,
            "team": self.current_player.team,
            "from": piece.position if action_type == "move" else None,
            "to": (x, y),
        }

        self.next_turn()

    def place_piece(self, piece: Piece, position: tuple[int, int]):
        """Places a captured piece on the board."""
        if not piece.position and position and piece.can_place(position, self.board.pieces):
            if not self.board.get_piece(position):
                piece.on_place(position, self.board.pieces)  # Update piece state
                self.board.on_place_piece(piece, position)  # Add to board
                self.current_player.on_place_piece(piece)  # Remove from captured pieces
            else:
                raise ValueError("Position is already occupied.")
        else:
            raise ValueError("Invalid piece placement.")
        
    def special_processing(self, new_position, prev_piece, prev_pieces):
        if isinstance(prev_piece, ChessKing):
            rook = ChessKing.get_castling_partner(prev_piece.position, new_position, prev_piece.team, self.board.size, prev_pieces)
            if rook and isinstance(rook, ChessRook):
                position = rook.get_after_castling_position(prev_piece.position, prev_pieces)
                self.move_piece(rook, position, prev_pieces)
        elif isinstance(prev_piece, ChessPawn):
            pawn = ChessPawn.get_en_passant_target(prev_piece.team, new_position, prev_pieces)
            if pawn and isinstance(pawn, ChessPawn):
                self.capture_piece(pawn, prev_piece.team)

    def move_piece(self, piece: Piece, new_position: tuple[int, int], pieces=None):
        if not pieces:
            pieces = self.board.pieces
        
        """Moves a piece on the board."""
        if piece.position and new_position in piece.get_legal_moves(pieces):
            prev_pieces =  pieces
            prev_piece = copy.deepcopy(piece)

            captured_piece: Piece = self.board.get_piece(new_position)
            if captured_piece and captured_piece.team != piece.team:
                captured_piece = copy.deepcopy(captured_piece)
                self.capture_piece(captured_piece, piece.team)
                prev_pieces[captured_piece.position] = captured_piece

            self.board.on_move_piece(piece, piece.position, new_position)
            piece.on_move(new_position, prev_pieces)

            self.special_processing(new_position, prev_piece, prev_pieces)
        else:
            raise ValueError("Invalid move.")

    def capture_piece(self, piece: Piece, capturing_team):
        """Captures a piece and adds it to the current player's captured pieces."""
        self.board.on_capture_piece(piece.position)
        piece.on_captured(capturing_team)
        self.current_player.add_captured_piece(piece)

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
        return

        if self.check_repetition():
            self.game_set()
        else:
            self.step += 1

    def game_set(self):
        print("引き分け")

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
            "white_checked": False, # game_instance.white.checked,  # 仮にcheckedプロパティが存在する場合
            "black_checked": False, # game_instance.black.checked,  # 同上
            "game_result": None,  # ゲームの結果（引き分けなど）
            "error": None  # エラーメッセージ
        }

        return SendDataManager.create_game_data_dict(game_state)