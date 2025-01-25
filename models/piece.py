class Piece:
    __EVERY_DIRECTION = [(-1, -1), (0, -1), (1, -1),
                        (-1,  0),         (1,  0),
                        (-1,  1), (0,  1), (1,  1)]

    __UP_DOWN_LEFT_RIGHT = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
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


    def __lt__(self, other):
        """Compare pieces based on their IDs."""
        return self.piece_id < other.piece_id

    @property
    def EVERY_DIRECTION(self):
        return self.__EVERY_DIRECTION.copy()
    
    @property
    def UP_DOWN_LEFT_RIGHT(self):
        return self.__UP_DOWN_LEFT_RIGHT.copy()
    
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
        if is_valid_pieces and position in self.legal_moves(pieces):
            self.__last_move = (self.position)
            self.__position = position

        # 動けなくなる場合、強制的に成る
        if auto_promote and self.immobile_row and not self.is_behind_line(position[1], self.immobile_row):
            self.set_promote(True)

    def on_place(self, position, pieces: dict):
        if self.can_place(position, pieces):
            self.__position = position
            self.__last_move = position
            self.__is_rearranged = True

    def can_place(self, position, pieces: dict):
        return not self.is_banned_place and self.is_within_board(position) and not pieces.get(position) and (not self.immobile_row or self.is_behind_line(position[1], self.immobile_row))
    
    # 継承する
    def legal_moves(self, pieces: dict):
        return []
    
    def can_promote(self, y):
        """Check if the piece can be promoted."""
        return not self.is_banned_promote and self.promote_line and not self.is_behind_line(y, self.promote_line)

    def is_within_board(self, position):
        x, y = position
        return 0 <= x < self.board_size and 0 <= y < self.board_size
    
    def is_behind_line(self, y, line):
        return (self.team == 'white' and y >= line) or (self.team == 'black' and y <= self.board_size - line - 1)

    @staticmethod
    def adjust_position_for_team(position, team):
        x, y = position
        return (x, -y) if team == 'white' else position

    @staticmethod
    def adjust_positions_for_team(positions, team):
        return [Piece.adjust_position_for_team(pos, team) for pos in positions]

    def get_valid_moves(self, pieces: dict, positions=None, directions=None, length=None):
        moves = []

        if positions:
            positions = Piece.adjust_positions_for_team(positions, self.team)
            for dx, dy in positions:
                nx, ny = self.position[0] + dx, self.position[1] + dy
                if self.is_within_board((nx, ny)):
                    target_piece: Piece = pieces.get((nx, ny))
                    if not target_piece or target_piece.team != self.team:
                        moves.append((nx, ny))

        if directions:
            if not length:
                length = self.board_size
            length = min(length + 1, self.board_size)

            directions = Piece.adjust_positions_for_team(directions, self.team)
            for dx, dy in directions:
                for i in range(1, length):
                    nx, ny = self.position[0] + dx * i, self.position[1] + dy * i
                    if not self.is_within_board((nx, ny)):
                        break
                    target_piece = pieces.get((nx, ny))
                    if target_piece:
                        if target_piece.team != self.team:
                            moves.append((nx, ny))
                        break
                    moves.append((nx, ny))

        return moves

    @classmethod
    def get_instance(cls, piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row):
        return Piece(piece_id, position, team, board_size, promote_line, is_banned_place, is_banned_promote, is_promoted, immobile_row)
    
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