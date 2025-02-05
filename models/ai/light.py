from models.game.game import Game
from models.game.player import Player
from models.piece.piece import Piece
from models.piece.pieces_info import PIECE_VALUES, PROM_PIECE_VALUES
from models.type import LastMove

class LightPlayer:
    def __init__(self, player: Player):
        # キャプチャ済み駒を、駒の種類ごとに駒インスタンスのリストで管理する
        captured_pieces = {}
        for piece in player.captured_pieces:
            # もともとの駒は piece_id を保持しているものとする
            light_piece = LightPiece(piece.piece_id, piece.name, piece.team, piece.is_promoted, piece.is_first_move, piece.is_rearranged)
            if piece.name in captured_pieces:
                captured_pieces[piece.name].append(light_piece)
            else:
                captured_pieces[piece.name] = [light_piece]
        # 各リストを piece_id 昇順にソート
        for name in captured_pieces:
            captured_pieces[name].sort(key=lambda p: p.piece_id)
        self.captured_pieces: dict[str, list[LightPiece]] = captured_pieces

    def add_captured_piece(self, captured_piece):
        """捕獲した駒（LightPiece インスタンス）を追加する"""
        name = captured_piece.name
        if name in self.captured_pieces:
            self.captured_pieces[name].append(captured_piece)
            self.captured_pieces[name].sort(key=lambda p: p.piece_id)
        else:
            self.captured_pieces[name] = [captured_piece]

    def remove_captured_piece(self, name):
        """指定された名前の駒のうち、piece_id が最小のものを取り出す"""
        if name not in self.captured_pieces or not self.captured_pieces[name]:
            raise ValueError(f"No captured piece of type {name} available to place")
        return self.captured_pieces[name].pop(0)


class LightPiece:
    def __init__(self, piece_id, name, team, is_promoted, is_first_move, is_rearranged):
        if name not in PIECE_VALUES:
            raise ValueError(f"Invalid piece name: {name}")
        if team not in ["white", "black"]:
            raise ValueError("Invalid team. Expected 'white' or 'black'")

        self.piece_id = piece_id
        self.name = name
        self.team = team
        self.is_promoted = is_promoted
        self.is_first_move = is_first_move
        self.is_rearranged = is_rearranged
        self.value = PIECE_VALUES[self.name] if not is_promoted else PROM_PIECE_VALUES[self.name]

    def promote(self):
        if not self.is_promoted:
            self.is_promoted = True
            self.value = PROM_PIECE_VALUES[self.name]

    def demote(self):
        if self.is_promoted:
            self.is_promoted = False
            self.value = PIECE_VALUES[self.name]


class LightBoard:
    def __init__(self, game: Game, white_player: LightPlayer, black_player: LightPlayer):
        if not isinstance(game, Game):
            raise TypeError("Expected board to be an instance of Game")
        if not isinstance(white_player, LightPlayer) or not isinstance(black_player, LightPlayer):
            raise TypeError("Expected players to be instances of LightPlayer")
        
        # 盤上の駒を、もともとの piece_id を用いて LightPiece に変換する
        self.pieces: dict[tuple[int, int], LightPiece] = {
            pos: LightPiece(piece.piece_id, piece.name, piece.team, piece.is_promoted, piece.is_first_move, piece.is_rearranged)
            for pos, piece in game.board.pieces.items()
        }
        self.immobile_rows: dict[str, int] = {
            piece.name: piece.immobile_row for piece in game.board.pieces.values() if piece.immobile_row
        }
        self.placeable_state: dict[str, bool] = {
            piece.name: not piece.is_banned_place for piece in [*game.board.pieces.values(), *game.black.captured_pieces, *game.white.captured_pieces]
        }
        self.board_size = game.board.size
        self.white_player = white_player
        self.black_player = black_player
        self.history = []  # 履歴は後の undo_action のために保持

    def get_player(self, team):
        if team not in ["white", "black"]:
            raise ValueError("Invalid team. Expected 'white' or 'black'")
        return self.white_player if team == "white" else self.black_player

    def move(self, team, from_pos, to_pos, promote=False):
        if team not in ["white", "black"]:
            raise ValueError("Invalid team. Expected 'white' or 'black'")
        if from_pos not in self.pieces:
            raise KeyError(f"No piece at position {from_pos}")
        if not isinstance(to_pos, tuple) or len(to_pos) != 2:
            raise ValueError("Invalid to_pos. Expected a tuple of (x, y)")

        piece = self.pieces[from_pos]
        enemy = self.pieces.get(to_pos)

        # 捕獲処理：敵の駒が存在する場合、その駒インスタンスをキャプチャ済みリストに追加する
        if enemy:
            player = self.get_player(team)
            player.add_captured_piece(enemy)

        # 移動前の状態を保存
        was_first_move = piece.is_first_move
        piece.is_first_move = False

        # 駒を移動
        self.pieces[to_pos] = self.pieces.pop(from_pos)

        # 昇格処理
        was_promoted = piece.is_promoted
        if promote and not piece.is_promoted:
            piece.promote()

        # 履歴に記録（captured_piece は存在すれば LightPiece インスタンス）
        self.history.append(("move", team, from_pos, to_pos, enemy, was_promoted, was_first_move))

    def place(self, team, name, position):
        if team not in ["white", "black"]:
            raise ValueError("Invalid team. Expected 'white' or 'black'")
        if name not in PIECE_VALUES:
            raise ValueError(f"Invalid piece name: {name}")
        if position in self.pieces:
            raise ValueError(f"Position {position} is already occupied")
        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Invalid position. Expected a tuple of (x, y)")

        player = self.get_player(team)
        # キャプチャ済みの駒から、piece_id が最も小さいものを取り出す
        
        captured_piece = player.remove_captured_piece(name)
        # 取得した駒は、配置するために属性を更新する（例えば所属チームや初手フラグなど）
        captured_piece.team = team
        captured_piece.is_promoted = False
        captured_piece.is_first_move = False
        captured_piece.is_rearranged = True

        self.pieces[position] = captured_piece
        # 履歴には、配置した駒そのものを記録しておく
        self.history.append(("place", team, captured_piece, position))

    def undo_action(self):
        if not self.history:
            raise ValueError("No actions to undo")

        last_action = self.history.pop()
        action_type = last_action[0]

        if action_type == "move":
            _, team, from_pos, to_pos, captured_piece, was_promoted, was_first_move = last_action
            piece = self.pieces[to_pos]

            # 移動を取り消し
            self.pieces[from_pos] = self.pieces.pop(to_pos)
            if captured_piece:
                # 捕獲されていた駒を盤上に戻す
                self.pieces[to_pos] = captured_piece
                player = self.get_player(team)
                # キャプチャ済みリストから該当の駒（piece_id で照合）を削除する
                if captured_piece.name in player.captured_pieces:
                    lst = player.captured_pieces[captured_piece.name]
                    for i, p in enumerate(lst):
                        if p.piece_id == captured_piece.piece_id:
                            lst.pop(i)
                            break

            # 昇格状態の取り消し
            if was_promoted != piece.is_promoted:
                piece.demote()

            # 初手フラグの復元
            piece.is_first_move = was_first_move

        elif action_type == "place":
            _, team, placed_piece, position = last_action
            # 盤上から配置した駒を取り除く
            del self.pieces[position]
            player = self.get_player(team)
            # 配置取り消しの場合、配置された駒をキャプチャ済みリストに戻す
            player.add_captured_piece(placed_piece)

    def get_last_move(self) -> LastMove:
        if len(self.history) == 0:
            return
        
        last_action = self.history[-1]

        if last_action[0] == "move":
            _, team, from_pos, to_pos, captured_piece, was_promoted, was_first_move = last_action
            last_action_piece = self.pieces.get(to_pos)

            if not last_action_piece:
                return None

            return {
                "action_type": "move",
                "piece_id": last_action_piece.piece_id,
                "piece_name": last_action_piece.name,
                "team": last_action_piece.team,
                "from_pos": from_pos,
                "to_pos": to_pos
            }
        elif last_action[0] == "place":
            _, team, placed_piece, position = last_action
            last_action_piece = self.pieces.get(position)

            return {
                "action_type": "move",
                "piece_id": last_action_piece.piece_id,
                "piece_name": last_action_piece.name,
                "team": team,
                "from_pos": None,
                "to_pos": placed_piece
            }