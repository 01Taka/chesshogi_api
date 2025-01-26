class Piece:
    def __init__(
            self,
            piece_id: str,
            position: None | tuple[int, int],
            team: str,
            board_size: int,
            promote_line: int,
            is_banned_place=False,
            is_banned_promote=False,
            is_promoted=False,
            immobile_row=None,
            last_move=None,
            is_rearranged=False
    ):
        self.__piece_id = piece_id
        self.__board_size = board_size
        self.__promote_line = promote_line
        self.__is_banned_place = is_banned_place
        self.__is_banned_promote = is_banned_promote
        self.__immobile_row = immobile_row
        self.__is_rearranged = is_rearranged

        self.__position = position
        self.__last_move = last_move
        self.__team = team
        self.__is_promoted = is_promoted

    # ---- Properties ----
    @property
    def piece_id(self):
        return self.__piece_id

    @property
    def position(self):
        return tuple(self.__position) if self.__position else None

    @property
    def last_move(self):
        return self.__last_move

    @property
    def team(self):
        return self.__team

    @team.setter
    def team(self, value):
        if value in ("black", "white"):
            self.__team = value

    @property
    def board_size(self):
        return self.__board_size

    @property
    def promote_line(self):
        return self.__promote_line

    @property
    def is_promoted(self):
        return self.__is_promoted

    @property
    def is_banned_place(self):
        return self.__is_banned_place

    @property
    def is_banned_promote(self):
        return self.__is_banned_promote

    @property
    def immobile_row(self):
        return self.__immobile_row

    @property
    def is_rearranged(self):
        return self.__is_rearranged

    @property
    def name(self):
        """Return the name of the piece class."""
        return self.__class__.__name__

    # ---- Magic Methods ----
    def __lt__(self, other):
        """Compare pieces based on their IDs."""
        return self.piece_id < other.piece_id

    # ---- Static Properties ----
    @staticmethod
    def EVERY_DIRECTION():
        return [(-1, -1), (0, -1), (1, -1),
                (-1,  0),         (1,  0),
                (-1,  1), (0,  1), (1,  1)].copy()

    @staticmethod
    def UP_DOWN_LEFT_RIGHT():
        return [(0, 1), (1, 0), (0, -1), (-1, 0)].copy()


    # ---- Primary Methods ----
    def set_promote(self, is_promote, prev_position_y=None):
        if is_promote:
            is_out_and_promote = prev_position_y and self.can_promote(prev_position_y)
            if self.can_promote(self.position[1]) or is_out_and_promote:
                self.__is_promoted = True
        else:
            self.__is_promoted = False

    def on_captured(self, captured_team):
        self.__position = None
        self.set_promote(False)
        self.team = captured_team

    def on_move(self, position, pieces: dict, auto_promote=True):
        is_valid_pieces = self.position and pieces.get(self.position) and pieces[self.position].piece_id == self.piece_id
        if is_valid_pieces and position in self.get_legal_moves(pieces):
            self.__last_move = (self.position)
            self.__position = position

        # Auto-promote if moving into an immobile position
        if auto_promote and self.immobile_row and not Piece.is_behind_line(self.team, self.board_size, position[1], self.immobile_row):
            self.set_promote(True)

    def on_place(self, position, pieces: dict):
        if self.can_place(position, pieces):
            self.__position = position
            self.__last_move = position
            self.__is_rearranged = True

    def can_place(self, position, pieces: dict) -> bool:
        is_within_board = Piece.is_within_board(self.board_size, position)
        is_empty_position = not pieces.get(position)
        is_valid_row = not self.immobile_row or Piece.is_behind_line(self.team, self.board_size, position[1], self.immobile_row)

        return (
            not self.is_banned_place
            and is_within_board
            and is_empty_position
            and is_valid_row
        )

    def can_promote(self, y):
        """Check if the piece can be promoted."""
        is_valid_row = self.promote_line and not Piece.is_behind_line(self.team, self.board_size, y, self.promote_line)
        return not self.is_banned_promote and is_valid_row

    def get_legal_moves(self, pieces: dict):
        if self.position:
            return self.get_legal_moves_static(self.position, self.team, self.is_promoted, self.board_size, pieces, not self.last_move, self.is_rearranged)
        else:
            return []

    # ---- Static Methods ----
    @staticmethod
    def is_within_board(board_size, position):
        x, y = position
        return 0 <= x < board_size and 0 <= y < board_size

    @staticmethod
    def is_behind_line(team, board_size, y, line):
        return (team == 'white' and y >= line) or (team == 'black' and y <= board_size - line - 1)
    
    @staticmethod
    def can_promote_static(team, from_y, to_y, board_size, promote_line):
        """Check if the piece can be promoted."""
        return promote_line and any(not Piece.is_behind_line(team, board_size, y, promote_line) for y in [from_y, to_y])

    @staticmethod
    def adjust_position_for_team(position, team):
        x, y = position
        return (x, -y) if team == 'white' else position

    @staticmethod
    def adjust_positions_for_team(positions, team):
        return [Piece.adjust_position_for_team(pos, team) for pos in positions]

    @staticmethod
    def get_relative_legal_moves(is_promoted):
        raise NotImplementedError("This method must be overridden in a subclass")

    @staticmethod
    def get_valid_moves(position, team, board_size, pieces: dict, positions=None, directions=None):
        moves = []

        if positions:
            positions = Piece.adjust_positions_for_team(positions, team)
            for dx, dy in positions:
                nx, ny = position[0] + dx, position[1] + dy
                if Piece.is_within_board(board_size, (nx, ny)):
                    target_piece: Piece = pieces.get((nx, ny))
                    if not target_piece or target_piece.team != team:
                        moves.append((nx, ny))

        if directions:
            directions = Piece.adjust_positions_for_team(directions, team)
            for dx, dy in directions:
                for i in range(1, board_size):
                    nx, ny = position[0] + dx * i, position[1] + dy * i
                    if not Piece.is_within_board(board_size, (nx, ny)):
                        break
                    target_piece = pieces.get((nx, ny))
                    if target_piece:
                        if target_piece.team != team:
                            moves.append((nx, ny))
                        break
                    moves.append((nx, ny))

        return moves
    
    # ---- Class Methods ----
    @classmethod
    def get_legal_moves_static(cls, position, team, is_promoted, board_size, pieces: dict, is_first_move=False, is_rearranged=False):
        positions, directions = cls.get_relative_legal_moves(is_promoted)
        return Piece.get_valid_moves(position, team, board_size, pieces, positions, directions)

    # ---- Factory Methods ----
    @classmethod
    def get_instance(cls, piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row):
        return Piece(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)

    # ---- Conversion Methods ----
    def to_dict(self):
        return {
            "class_name": self.__class__.__name__,
            "piece_id": self.__piece_id,
            "position": self.__position,
            "team": self.__team,
            "board_size": self.__board_size,
            "promote_line": self.__promote_line,
            "is_banned_place": self.__is_banned_place,
            "is_banned_promote": self.__is_banned_promote,
            "is_promoted": self.__is_promoted,
            "immobile_row": self.__immobile_row,
            "last_move": self.__last_move,
            "is_rearranged": self.__is_rearranged
        }
