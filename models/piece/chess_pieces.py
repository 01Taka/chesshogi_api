from models.piece.piece import Piece
from models.type import Pieces, LastMove

class ChessPiece(Piece):    
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=True, is_banned_promote=True, is_promoted=False, immobile_row=None, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

class ChessKing(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """King's legal moves: one square in any direction, plus expanded castling"""
        return Piece.EVERY_DIRECTION(), None

    @staticmethod
    def get_chess_king_relative_legal_moves(position, team, board_size, is_first_move, pieces):
        """King's legal moves: one square in any direction, plus expanded castling"""
        moves = Piece.EVERY_DIRECTION()  # 通常の動き
        if is_first_move:
            castling_moves = ChessKing.castling_moves(position, team, board_size, pieces)  # キャスリングの候補を取得
            moves.extend(castling_moves)
        return moves, None
    
    @classmethod
    def get_legal_moves_static(cls, position, team, is_promoted, board_size, pieces: Pieces, is_first_move=False, is_rearranged=False, last_move=None):
        positions, directions = ChessKing.get_relative_legal_moves(is_promoted)
        positions, directions = ChessKing.get_chess_king_relative_legal_moves(position, team, board_size, is_first_move, pieces)
        
        return Piece.get_valid_moves(position, team, board_size, pieces, positions, directions)

    @staticmethod
    def castling_moves(position, team, board_size, pieces: Pieces):
        """Check for castling moves and return possible moves"""
        moves = []
        for direction in [(1, 0), (-1, 0)]:
            if ChessKing.can_castle_in_direction(direction, position, team, board_size, pieces):
                moves.append((2 * direction[0], 2 * direction[1]))
        return moves

    @staticmethod
    def can_castle_in_direction(direction, position, team, board_size, pieces: Pieces):
        """Check if castling is possible in a given direction"""
        if ChessKing.is_under_attack(position, pieces):
            return False
        
        dx, dy = direction
        for i in range(1, board_size):
            nx, ny = position[0] + dx * i, position[1] + dy * i

            if not Piece.is_within_board(board_size, (nx, ny)) or ChessKing.is_under_attack((nx, ny), pieces):
                return False
            
            rook = pieces.get((nx, ny))
            if rook:
                if isinstance(rook, ChessRook) and not rook.last_position and rook.team == team:
                    return True
                else:
                    return False

        return False

    @staticmethod
    def is_under_attack(square, pieces):
        """Placeholder for checking if a square is under attack"""
        # TODO: Implement the actual logic
        return False
    
    @staticmethod
    def is_castling_move(current_position, target_position, team, board_size, pieces: Pieces):
        """Check if the move is a castling move"""
        if not pieces.get(target_position) and Piece.is_within_board(board_size, target_position):
            castling_moves = ChessKing.castling_moves(target_position, team, board_size, pieces) 
            return target_position in ((current_position[0] + x, current_position[1] + y) for x, y in castling_moves)
        else:
            return False
    
    
    @staticmethod
    def get_castling_partner(current_position, target_position, team, board_size, pieces: Pieces):
        """
        Get the rook involved in castling for the given castling move target_position.
        
        Args:
            pieces (Pieces): Current board state.
            position (tuple): Target position for the king's castling move.
        
        Returns:
            ChessRook: The rook involved in castling, or None if no such rook exists.
        """
        if not ChessKing.is_castling_move(current_position, target_position, team, board_size, pieces):
            return None
        
        # Determine direction of castling based on the target position
        dx = target_position[0] - current_position[0]
        direction = (1 if dx > 0 else -1, 0)  # Horizontal direction
        
        # Traverse along the direction to find the rook
        nx, ny = current_position[0] + direction[0], current_position[1] + direction[1]
        while Piece.is_within_board(board_size, (nx, ny)):
            piece = pieces.get((nx, ny))
            if piece:
                if isinstance(piece, ChessRook) and piece.team == team and not piece.last_position:
                    return piece
                else:
                    return None
            nx += direction[0]
            ny += direction[1]

        return None


class ChessQueen(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """Queen's legal moves: any number of squares in all directions"""
        return None, Piece.EVERY_DIRECTION()

class ChessRook(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """Rook's legal moves: any number of squares vertically or horizontally"""
        return None, Piece.UP_DOWN_LEFT_RIGHT()

    @staticmethod
    def is_vacant_between(position, direction, length, pieces: Pieces):
        dx, dy = max(min(direction[0], 1), -1), max(min(direction[1], 1), -1)
        if dx == 0 and dy == 0:
            return True
        
        for i in range(1, length):
            nx, ny = position[0] + dx * i, position[1] + dy * i
            if pieces.get((nx, ny)):
                return False
            return True
    
    @staticmethod
    def get_after_castling_position(rook_position, king_position: tuple):
        dx = king_position[0] - rook_position[0]
        dy = king_position[1] - rook_position[1]
        normalized_direction = max(min(dx, 1), -1), max(min(dy, 1), -1)

        if dx != 0 and dy != 0:
            return
        
        # if ChessRook.is_vacant_between(rook_position, normalized_direction, max(abs(dx), abs(dy)), pieces):
        position = (king_position[0] - normalized_direction[0], king_position[1] - normalized_direction[1]) # キングのもとの位置の一つとなり

        return position


class ChessBishop(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """Bishop's legal moves: any number of squares diagonally"""
        return None, [(-1, -1), (1, -1), (-1, 1), (1, 1)]

class ChessKnight(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """Knight's legal moves: L-shaped moves"""
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                      (1, -2), (1, 2), (2, -1), (2, 1)]
        return directions, None

class ChessPawn(ChessPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=True, is_banned_promote=False, is_promoted=False, immobile_row=1, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(_):
        return [(0, 1)], None
    
    @staticmethod
    def get_chess_pawn_relative_legal_moves(is_promoted, is_rearranged, position, team, pieces, is_first_move, last_move: LastMove):
        """Pawn's legal moves: forward 1 square, optionally 2 squares on first move, diagonal capture"""
        if is_promoted:
            positions = None if not is_rearranged else Piece.EVERY_DIRECTION()
            directions = Piece.EVERY_DIRECTION() if not is_rearranged else []
            return positions, directions
        else:
            moves = []
            x, y = position
            direction = 1 if team == 'black' else -1

            # Forward move
            if not pieces.get((x, y + direction)):
                moves.append(((0, 1)))
                if is_first_move and not pieces.get((x, y + 2 * direction)):
                    moves.append((0, 2))

            # Diagonal captures and en passant
            for dx in [-1, 1]:
                to_position = (x + dx, y + direction)
                target = pieces.get(to_position)
                if target and target.team != team:
                    moves.append((dx, 1))
            
            # アンパッサン
            _, _, capture_pos = ChessPawn.get_en_passant(team, position, pieces, last_move)
            if capture_pos:
                moves.append((capture_pos[0] - position[0], 1))
            
            return moves, None
    
    @staticmethod
    def get_en_passant(team, from_position, pieces: Pieces, last_move: LastMove):
        if not last_move:
            return None, None, None
        
        # last_move に移動先が存在しない場合はすぐに終了
        to_pos = last_move.get("to_pos")
        from_pos = last_move.get("from_pos")
        if not to_pos or not from_pos:
            return None, None, None

        # 比較しやすいようにタプルに変換
        to_pos = tuple(to_pos)
        from_pos = tuple(from_pos)
        offset = -1 if team == 'white' else 1

        # 前に2マス動いていない場合早期リターン
        if from_pos[1] != to_pos[1] + (offset * 2):
            return None, None, None

        # 横方向の左右に対してチェックする
        for dx in (-1, 1):
            target_pos = (from_position[0] + dx, from_position[1])
            if target_pos == to_pos:
                target = pieces.get(target_pos)
                # 対象の駒が存在し、かつ直前の移動で動いた駒と一致するか確認
                if target and target.piece_id == last_move.get("piece_id"):
                    # アンパッサンによる捕獲先の位置を決定
                    capture_pos = (target_pos[0], target_pos[1] + offset)
                    return target, target_pos, capture_pos

        return None, None, None

        
    @classmethod
    def get_legal_moves_static(cls, position, team, is_promoted, board_size, pieces: Pieces, is_first_move=False, is_rearranged=False, last_move=None):
        positions, directions = ChessPawn.get_relative_legal_moves(is_promoted)
        positions, directions = ChessPawn.get_chess_pawn_relative_legal_moves(is_promoted, is_rearranged, position, team, pieces, is_first_move, last_move)
        return Piece.get_valid_moves(position, team, board_size, pieces, positions, directions)

class ChessPillar(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """Bishop's legal moves: any number of squares diagonally"""
        positions = [[1, 0], [2, 0], [0, 1], [0, 2], [-1, 0], [-2, 0], [0, -1], [0, -2]]
        return positions, None

class ChessWisp(ChessPiece):
    @staticmethod
    def get_relative_legal_moves(_):
        """Bishop's legal moves: any number of squares diagonally"""
        positions = [[1, 1], [2, 2], [-1, 1], [-2, 2], [-1, -1], [-2, -2], [1, -1], [2, -2]]
        return positions, None

class ChessLance(ChessPiece):
    def __init__(self, piece_id, team, board_size, promote_line, is_banned_place=True, is_banned_promote=False, is_promoted=False, immobile_row=1, last_position=None, is_rearranged=False):
        super().__init__(piece_id, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row, last_position, is_rearranged)

    @staticmethod
    def get_relative_legal_moves(is_promoted):
        """Bishop's legal moves: any number of squares diagonally"""
        directions = [(0, 1)] if not is_promoted else None
        positions = None if not is_promoted else Piece.EVERY_DIRECTION()
        return positions, directions