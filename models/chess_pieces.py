from models.piece import Piece

class ChessPiece(Piece):    
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=True, is_banned_promote=True, is_promoted=False, immobile_row=None):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

class ChessKing(ChessPiece):
    def legal_moves(self, pieces: dict):
        """King's legal moves: one square in any direction, plus expanded castling"""
        moves = self.EVERY_DIRECTION.copy()  # 通常の動き
        if not self.last_move:
            castling_moves = self.castling_moves(pieces)  # キャスリングの候補を取得
            moves.extend(castling_moves)
        return self.get_valid_moves(pieces, positions=moves)

    def castling_moves(self, pieces: dict):
        """Check for castling moves and return possible moves"""
        moves = []
        for direction in self.UP_DOWN_LEFT_RIGHT:
            if self.can_castle_in_direction(direction, pieces):
                moves.append((2 * direction[0], 2 * direction[1]))
        return moves

    def can_castle_in_direction(self, direction, pieces: dict):
        """Check if castling is possible in a given direction"""
        if self.is_under_attack(self.position, pieces):
            return False
        
        dx, dy = direction
        for i in range(1, self.board_size):
            nx, ny = self.position[0] + dx * i, self.position[1] + dy * i

            if not self.is_within_board((nx, ny)) or self.is_under_attack((nx, ny), pieces):
                return False
            
            rook = pieces.get((nx, ny))
            if rook:
                if isinstance(rook, ChessRook) and not rook.last_move and rook.team == self.team:
                    return True
                else:
                    return False

        return False

    def is_under_attack(self, square, pieces):
        """Placeholder for checking if a square is under attack"""
        # TODO: Implement the actual logic
        return False
    
    def is_castling_move(self, position, pieces):
        """Check if the move is a castling move"""
        castling_moves = self.castling_moves(pieces)
        return position in self.get_valid_moves(pieces, castling_moves)
    
    def get_castling_partner(self, position, pieces: dict[(int, int), Piece]):
        """
        Get the rook involved in castling for the given castling move position.
        
        Args:
            pieces (dict): Current board state.
            position (tuple): Target position for the king's castling move.
        
        Returns:
            ChessRook: The rook involved in castling, or None if no such rook exists.
        """
        if not self.is_castling_move(position, pieces):
            return None
        
        # Determine direction of castling based on the target position
        dx = position[0] - self.position[0]
        direction = (1 if dx > 0 else -1, 0)  # Horizontal direction
        
        # Traverse along the direction to find the rook
        nx, ny = self.position[0] + direction[0], self.position[1] + direction[1]
        while self.is_within_board((nx, ny)):
            piece = pieces.get((nx, ny))
            if piece:
                if isinstance(piece, ChessRook) and piece.team == self.team and not piece.last_move:
                    return piece
                else:
                    return None
            nx += direction[0]
            ny += direction[1]

        return None


class ChessQueen(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Queen's legal moves: any number of squares in all directions"""
        directions = self.EVERY_DIRECTION
        return self.get_valid_moves(pieces, directions=directions)

class ChessRook(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Rook's legal moves: any number of squares vertically or horizontally"""
        directions = self.UP_DOWN_LEFT_RIGHT
        return self.get_valid_moves(pieces, directions=directions)

    def is_vacant_between(self, direction, length, pieces: dict):
        dx, dy = max(min(direction[0], 1), -1), max(min(direction[1], 1), -1)
        if dx == 0 and dy == 0:
            return True
        
        for i in range(1, length):
            nx, ny = self.position[0] + dx * i, self.position[1] + dy * i
            if pieces.get((nx, ny)):
                return False
            return True
    
    def get_after_castling_position(self, king_position: tuple, pieces: dict):
        dx = king_position[0] - self.position[0]
        dy = king_position[1] - self.position[1]
        normalized_direction = max(min(dx, 1), -1), max(min(dy, 1), -1)

        if dx != 0 and dy != 0:
            return
        
        if self.is_vacant_between(normalized_direction, max(abs(dx), abs(dy)), pieces):
            position = (king_position[0] - normalized_direction[0], king_position[1] - normalized_direction[1]) # キングのもとの位置の一つとなり

        return position


class ChessBishop(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Bishop's legal moves: any number of squares diagonally"""
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        return self.get_valid_moves(pieces, directions=directions)

class ChessKnight(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Knight's legal moves: L-shaped moves"""
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                      (1, -2), (1, 2), (2, -1), (2, 1)]
        return self.get_valid_moves(pieces, positions=directions)

class ChessPawn(ChessPiece):
    def __init__(self, piece_id, position, team, board_size, promote_line, is_banned_place=True, is_banned_promote=False, is_promoted=False, immobile_row=1):
        super().__init__(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)
        self.__initial_row = position[1] if position and not self.last_move else None

    @property
    def initial_row(self):
        return self.__initial_row
    
    def on_place(self, position, pieces):
        self.__initial_row = None
        return super().on_place(position, pieces)

    def legal_moves(self, pieces: dict):
        """Pawn's legal moves: forward 1 square, optionally 2 squares on first move, diagonal capture, and en passant"""
        if self.is_promoted:
            return self.get_valid_moves(pieces, directions=self.EVERY_DIRECTION)
        else:
            moves = []
            x, y = self.position
            direction = 1 if self.team == 'black' else -1

            # Forward move
            if not pieces.get((x, y + direction)):
                moves.append((x, y + direction))
                if self.initial_row and self.initial_row == y and not pieces.get((x, y + 2 * direction)):
                    moves.append((x, y + 2 * direction))

            # Diagonal captures and en passant
            for dx in [-1, 1]:
                target_pos = (x + dx, y + direction)
                target = pieces.get(target_pos)
                if target and target.team != self.team:
                    moves.append(target_pos)
                elif self.get_en_passant_target(target_pos, pieces):
                    moves.append(target_pos)

            return moves

    def get_en_passant_target(self, target_pos, pieces: dict):
        """Check if a given move is an en passant move."""
        direction = 1 if self.team == 'black' else -1
        target = pieces.get((target_pos[0], target_pos[1] - direction))  # ターゲットの位置
        if target and isinstance(target, ChessPawn) and target.team != self.team:
            if target.last_move and target.position and abs(target.last_move[1] - target.position[1]) == 2:
                return target
        return None


class ChessPillar(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Bishop's legal moves: any number of squares diagonally"""
        directions = self.UP_DOWN_LEFT_RIGHT
        return self.get_valid_moves(pieces, directions=directions, length=2)

class ChessWisp(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Bishop's legal moves: any number of squares diagonally"""
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        return self.get_valid_moves(pieces, directions=directions, length=2)

class ChessLance(ChessPiece):
    def legal_moves(self, pieces: dict):
        """Bishop's legal moves: any number of squares diagonally"""
        directions = [(0, 1)]
        return self.get_valid_moves(pieces, directions=directions) 