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
        moves, _ = self.get_legal_moves(pieces)
        if is_valid_pieces and position in moves:
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
            return [], []

    # ---- Static Methods ----
    @staticmethod
    def is_within_board(board_size, position):
        x, y = position
        return 0 <= x < board_size and 0 <= y < board_size

    @staticmethod
    def is_behind_line(team, board_size, y, line):
        return (team == 'white' and y >= line) or (team == 'black' and y <= board_size - line - 1)

    @staticmethod
    def get_coordinates_between_points(start, end):
        x1, y1 = start
        x2, y2 = end

        # x, y の進行方向を決定（1, -1, または 0）
        dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
        dy = 1 if y2 > y1 else -1 if y2 < y1 else 0

        # 8方向に該当しない場合は空リストを返す
        if (dx, dy) not in [(0, 1), (1, 0), (0, -1), (-1, 0),   # 上, 右, 下, 左
                            (1, 1), (1, -1), (-1, -1), (-1, 1)]: # 右上, 右下, 左下, 左上
            return []

        # 経路の座標リスト
        coordinates = []

        # 現在位置
        x, y = x1, y1

        # ゴールまで進める
        while (x, y) != (x2, y2):
            x += dx
            y += dy
            coordinates.append((x, y))

        return coordinates
    
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

        ally_blocks = []

        if positions:
            positions = Piece.adjust_positions_for_team(positions, team)
            for dx, dy in positions:
                nx, ny = position[0] + dx, position[1] + dy
                if Piece.is_within_board(board_size, (nx, ny)):
                    target_piece: Piece = pieces.get((nx, ny))
                    if not target_piece or target_piece.team != team:
                        moves.append((nx, ny))
                    else:
                        ally_blocks.append((nx, ny))

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
                        else:
                            ally_blocks.append((nx, ny))
                        break
                    moves.append((nx, ny))

        return moves, ally_blocks
    
    @staticmethod
    def get_piece_move_type_by_name(name):
        slide_pieces = ["ShogiLance", "ShogiRook", "ShogiBishop", "ShogiPhoenix", "ChessRook", "ChessBishop", "ChessQueen", "ChessLance"]
        if name in slide_pieces:
            return "slide"
        else:
            return "step"
    
    @staticmethod
    def find_moves_to_escape_check(king_pos, enemy_moves: dict, board_size):
        all_enemy_movables = sum([enemy_move["moves"] for enemy_move in enemy_moves], [])
        king_movables = []

        # 王が駒の効きの範囲外に出られるか計算
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = king_pos[0] + dx, king_pos[1] + dy
                if Piece.is_within_board(board_size, (x, y)) and (x, y) not in all_enemy_movables:
                    king_movables.append((x, y))
        
        other_piece_movables = []
        check_count = 0

        for enemy_move in enemy_moves:
            position, moves, move_type = enemy_move["position"], enemy_move["moves"], enemy_move["move_type"]
            if king_pos not in moves:
                continue

            check_count += 1

            # 他の駒が王手している駒を取ることで王手を回避する手を追加
            other_piece_movables.append(position)

            if move_type == "slide":
                dx, dy = position[0] - king_pos[0], position[1] - king_pos[1]
                opp_x = 0 if dx == 0 else -1 if dx > 0 else 1
                opp_y = 0 if dy == 0 else -1 if dy > 0 else 1
                # 直線移動の駒は後ろに動いても取られるので、敵の駒と反対方向の移動可能マスを削除
                opposite_pos = (king_pos[0] + opp_x, king_pos[1] + opp_y)
                if opposite_pos in king_movables:
                    king_movables.remove(opposite_pos)

                # 王と直線移動の駒の間に駒が移動することで王手を回避する手を追加
                between_positions = Piece.get_coordinates_between_points(king_pos, position)
                other_piece_movables.extend(between_positions)

        if check_count == 0:
            return None, None, "free"

        # 2つ以上の駒から王手されている場合、駒を取っての王手回避はできないので削除
        if check_count > 1:
            other_piece_movables.clear()

        state = "checkmate" if not king_movables and not other_piece_movables else "check"
        
        return king_movables, other_piece_movables, state
    
    # ---- Class Methods ----
    @classmethod
    def get_legal_moves_static(cls, position, team, is_promoted, board_size, pieces: dict, is_first_move=False, is_rearranged=False):
        positions, directions = cls.get_relative_legal_moves(is_promoted)
        return Piece.get_valid_moves(position, team, board_size, pieces, positions, directions)
    
    @classmethod
    def can_place_static(cls, position: tuple[int, int], team, board_size, pieces: dict, immobile_row=None):
        is_within_board = Piece.is_within_board(board_size, position)
        is_empty_position = not pieces.get(position)
        is_valid_row = not immobile_row or Piece.is_behind_line(team, board_size, position[1], immobile_row)

        return (
            is_within_board
            and is_empty_position
            and is_valid_row
        )

    @classmethod
    def get_legal_places_static(cls, team, board_size, pieces: dict, immobile_row=None) -> list[tuple[int, int]]:
        positions = []
        for x in range(board_size):
            for y in range(board_size):
                if cls.can_place_static((x, y), team, board_size, pieces, immobile_row):
                    positions.append((x, y))
        return positions
    
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
