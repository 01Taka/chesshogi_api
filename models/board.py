from models.piece import Piece
from models.board_initializer import BoardInitializer

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
    def pieces(self):
        return dict(self.__pieces)

    def on_place_piece(self, piece: Piece, position):
        if not self.get_piece(position):  
            self.__pieces[position] = piece

    def on_move_piece(self, piece: Piece, prev_position, new_position):
        captured_piece: Piece = self.get_piece(new_position)
        if captured_piece:
            self.on_capture_piece(captured_piece.position)

        self.__pieces.pop(prev_position, None)
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
