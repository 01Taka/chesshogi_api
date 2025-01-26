from models.piece import Piece
from models.game.board_initializer import BoardInitializer
from models.piece.pieces_info import PIECE_CLASSES
import json

class Board:
    def __init__(self, board_type: str, black_board: str, white_board: str, black_placeable: bool, white_placable: bool):
        size, pieces = BoardInitializer.get_board(board_type, black_board, white_board, black_placeable, white_placable)

        self.__board_type = board_type
        self.__black_board = black_board
        self.__white_board = white_board
        self.__size = size
        self.__pieces = pieces

    @property
    def board_type(self):
        return self.__board_type

    @property
    def black_board(self):
        return self.__black_board

    @property
    def white_board(self):
        return self.__white_board
        
    @property
    def size(self):
        return self.__size
    
    @property
    def pieces(self) -> dict[(int, int), Piece]:
        return dict(self.__pieces)

    def on_place_piece(self, piece: Piece, position):
        if not self.get_piece(position):  
            self.__pieces[position] = piece

    def on_move_piece(self, piece: Piece, prev_position, new_position):
        captured_piece: Piece = self.get_piece(new_position)
        if captured_piece:
            self.on_capture_piece(captured_piece.position)

        self.__pieces.pop(tuple(prev_position), None)
        self.__pieces[new_position] = piece
    
    def on_capture_piece(self, position):
        self.__pieces.pop(position, None)

    def get_piece(self, position):
        """
        Returns the piece at the given position (x, y), or None if unoccupied.
        """
        x, y = position
        return self.pieces.get((x, y))

    def get_piece_by_id(self, piece_id):
        """
        Finds and returns a piece by its unique ID.
        """
        return next((piece for piece in self.pieces.values() if piece.piece_id == piece_id), None)



    # タプル[(int, int)]を文字列に変換してエンコードする関数
    @staticmethod
    def encode_tuple(int_tuple):
        # タプル[(int, int)]を文字列形式に変換
        return json.dumps([str(i) for i in int_tuple])  # [str(i) for i in int_tuple]で各要素を文字列に変換

    @staticmethod
    # エンコードされた文字列を元のタプル[(int, int)]にデコードする関数
    def decode_tuple(encoded_str):
        # エンコードされた文字列をJSONとしてデコードし、元のタプル形式に戻す
        decoded_list = json.loads(encoded_str)
        return tuple(int(i) for i in decoded_list)  # 各要素を整数に戻してタプルに変換

    @staticmethod
    def piece_from_dict(data):
        PieceClass = PIECE_CLASSES[data["class_name"]]

        return PieceClass(
            piece_id=data["piece_id"],
            position=data["position"],
            team=data["team"],
            board_size=data["board_size"],
            promote_line=data["promote_line"],
            is_banned_place=data["is_banned_place"],
            is_banned_promote=data["is_banned_promote"],
            is_promoted=data["is_promoted"],
            immobile_row=data["immobile_row"],
            last_move=data["last_move"],
            is_rearranged=data["is_rearranged"]
        )

    def to_dict(self):
        return {
            "board_type": self.__board_type,
            "black_board": self.__black_board,
            "white_board": self.__white_board,
            "size": self.__size,
            "pieces": {Board.encode_tuple(position): piece.to_dict() for position, piece in self.__pieces.items()},
        }

    @staticmethod
    def from_dict(data):
        pieces = {Board.decode_tuple(position): Board.piece_from_dict(piece_data) for position, piece_data in data["pieces"].items()}
        board = Board(
            board_type=data["board_type"],
            black_board=data["black_board"],
            white_board=data["white_board"],
            black_placeable=False,  # ここでは適切な値を設定してください
            white_placable=False,   # 同様に適切な値を設定
        )
        board.__pieces = pieces
        return board

