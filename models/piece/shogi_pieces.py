from models.piece.piece import Piece 
from models.type import Pieces

class ShogiPiece(Piece):
    DEFAULT_PROMOTE_MOVES = [
        (-1, 1), (0, 1), (1, 1),
        (-1, 0),        (1, 0),
               (0, -1)
    ]

class ShogiKing(ShogiPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=False, is_banned_promote=True, is_promoted=False, immobile_row=None, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(_):
        """王の合法手: 周囲1マス"""
        return Piece.EVERY_DIRECTION(), None

class ShogiRook(ShogiPiece):
    @staticmethod
    def get_relative_legal_moves(is_promoted):
        """飛車の合法手: 縦横全て"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        positions = None if not is_promoted else [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        return positions, directions

class ShogiBishop(ShogiPiece):
    @staticmethod
    def get_relative_legal_moves(is_promoted):
        """角行の合法手: 斜め全て"""
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        positions = None if not is_promoted else [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return positions, directions

class ShogiPawn(ShogiPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=False, is_banned_promote=False, is_promoted=False, immobile_row=1, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(is_promoted):
        """歩兵の合法手: 前方1マス"""
        directions = [(0, 1)] if not is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return directions, None
    
    @staticmethod
    def has_pawn_in_column(team, x, pieces: Pieces):
        return any(piece.name == "ShogiPawn" and piece.team == team and not piece.is_promoted and pos[0] == x for pos, piece in pieces.items())

    def can_place(self, position, pieces: Pieces):
        return super().can_place(position, pieces) and not ShogiPawn.has_pawn_in_column(self.team, position[0], pieces)
    
    @classmethod
    def can_place_static(cls, position, team, board_size, pieces: Pieces, immobile_row=None):
        return super().can_place_static(position, team, board_size, pieces, immobile_row) and not ShogiPawn.has_pawn_in_column(team, position[0], pieces)

class ShogiLance(ShogiPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=False, is_banned_promote=False, is_promoted=False, immobile_row=1, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(is_promoted):
        directions = [(0, 1)] if not is_promoted else None
        positions = None if not is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return positions, directions

class ShogiKnight(ShogiPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=False, is_banned_promote=False, is_promoted=False, immobile_row=2, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(is_promoted):
        """桂馬の合法手: 前方2マス+斜め1マス"""
        directions = [(-1, 2), (1, 2)] if not is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return directions, None

class ShogiGold(ShogiPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=False, is_banned_promote=True, is_promoted=False, immobile_row=None, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(_):
        """金将の合法手: 前後左右と斜め前"""
        directions = ShogiPiece.DEFAULT_PROMOTE_MOVES
        return directions, None

class ShogiSilver(ShogiPiece):
    @staticmethod
    def get_relative_legal_moves(is_promoted):
        """銀将の合法手: 前後斜め"""
        default_directions = [(-1, 1), (0, 1), (1, 1),
                            (-1, -1),         (1, -1)]
        directions = default_directions if not is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return directions, None

class ShogiPhoenix(ShogiPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """鳳凰の合法手: 縦横斜め全て"""
        directions = Piece.EVERY_DIRECTION()
        return None, directions
    
class ShogiJumper(ShogiPiece):
    @staticmethod
    def get_relative_legal_moves(is_promoted):
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                      (1, -2), (1, 2), (2, -1), (2, 1)]
        if is_promoted:
            directions.extend(Piece.UP_DOWN_LEFT_RIGHT())

        return directions, None
