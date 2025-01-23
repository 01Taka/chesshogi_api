from models.piece import Piece 

class ShogiPiece(Piece):
    DEFAULT_PROMOTE_MOVES = [
        (-1, 1), (0, 1), (1, 1),
        (-1, 0),        (1, 0),
               (0, -1)
    ]

class ShogiKing(ShogiPiece):
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=False, is_banned_promote=True, is_promoted=False, immobile_row=None):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

    def legal_moves(self, pieces: dict):
        """王の合法手: 周囲1マス"""
        directions = self.EVERY_DIRECTION
        return self.get_valid_moves(pieces, positions=directions)

class ShogiRook(ShogiPiece):
    def legal_moves(self, pieces: dict):
        """飛車の合法手: 縦横全て"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        positions = None if not self.is_promoted else [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        return self.get_valid_moves(pieces, positions=positions, directions=directions)

class ShogiBishop(ShogiPiece):
    def legal_moves(self, pieces: dict):
        """角行の合法手: 斜め全て"""
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        positions = None if not self.is_promoted else [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return self.get_valid_moves(pieces, positions=positions, directions=directions)

class ShogiPawn(ShogiPiece):
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=False, is_banned_promote=False, is_promoted=False, immobile_row=1):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

    def legal_moves(self, pieces: dict):
        """歩兵の合法手: 前方1マス"""
        directions = [(0, 1)] if not self.is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return self.get_valid_moves(pieces, positions=directions)
    
    def has_pawn_in_column(self, x, pieces: dict):
        return any(isinstance(piece, ShogiPawn) and piece.team == self.team and piece.position[0] == x for piece in pieces)

    def can_place(self, position, pieces: dict):
        return super().can_place(position, pieces) and not self.has_pawn_in_column(position[0], pieces)

class ShogiLance(ShogiPiece):
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=False, is_banned_promote=False, is_promoted=False, immobile_row=1):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

    def legal_moves(self, pieces: dict):
        directions = [(0, 1)] if not self.is_promoted else None
        positions = None if not self.is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return self.get_valid_moves(pieces, positions=positions, directions=directions)

class ShogiKnight(ShogiPiece):
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=False, is_banned_promote=False, is_promoted=False, immobile_row=2):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

    def legal_moves(self, pieces: dict):
        """桂馬の合法手: 前方2マス+斜め1マス"""
        directions = [(-1, 2), (1, 2)] if not self.is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return self.get_valid_moves(pieces, positions=directions)

class ShogiGold(ShogiPiece):
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=False, is_banned_promote=True, is_promoted=False, immobile_row=None):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

    def legal_moves(self, pieces: dict):
        """金将の合法手: 前後左右と斜め前"""
        directions = ShogiPiece.DEFAULT_PROMOTE_MOVES
        return self.get_valid_moves(pieces, positions=directions)

class ShogiSilver(ShogiPiece):
    def legal_moves(self, pieces: dict):
        """銀将の合法手: 前後斜め"""
        default_directions = [(-1, 1), (0, 1), (1, 1),
                            (-1, -1),         (1, -1)]
        directions = default_directions if not self.is_promoted else ShogiPiece.DEFAULT_PROMOTE_MOVES
        return self.get_valid_moves(pieces, positions=directions)

class ShogiPhoenix(ShogiPiece):
    def legal_moves(self, pieces: dict):
        """鳳凰の合法手: 縦横斜め全て"""
        directions = self.EVERY_DIRECTION
        return self.get_valid_moves(pieces, directions=directions)
    
class ShogiJumper(ShogiPiece):
    def legal_moves(self, pieces: dict):
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                      (1, -2), (1, 2), (2, -1), (2, 1)]
        if self.is_promoted:
            directions.extend(self.UP_DOWN_LEFT_RIGHT)

        return self.get_valid_moves(pieces, positions=directions)