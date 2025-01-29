from models.game.board import Board
from models.game.game import Game
from models.game.player import Player
from models.piece.pieces_info import PIECE_VALUES, PROM_PIECE_VALUES

class LightPlayer():
    def __init__(self, player: Player):
        captured_pieces = {}
        for piece in player.captured_pieces:
            if piece.name in captured_pieces:
                captured_pieces[piece.name] += 1
            else:
                captured_pieces[piece.name] = 1
        
        self.captured_pieces: dict[str, int] = captured_pieces
    
    def add_captured_piece(self, name):
        if name in self.captured_pieces:
            self.captured_pieces[name] += 1
        else:
            self.captured_pieces[name] = 1

class LightPiece:
    def __init__(self, name, team, is_promoted, is_first_move, is_rearranged):
        if name not in PIECE_VALUES:
            raise ValueError(f"Invalid piece name: {name}")
        if team not in ["white", "black"]:
            raise ValueError("Invalid team. Expected 'white' or 'black'")
        
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
        
        self.pieces: dict[tuple[int, int], LightPiece] = {
            pos: LightPiece(piece.name, piece.team, piece.is_promoted, not piece.last_move, piece.is_rearranged)
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
        self.history = []

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

        # Capture enemy piece if present
        if enemy:
            player = self.get_player(team)
            player.add_captured_piece(enemy.name)

        # Update piece first move status
        was_first_move = piece.is_first_move
        piece.is_first_move = False

        # Move piece
        self.pieces[to_pos] = self.pieces.pop(from_pos)

        # Promotion
        was_promoted = piece.is_promoted
        if promote and not piece.is_promoted:
            piece.promote()

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
        if player.captured_pieces.get(name, 0) <= 0:
            raise ValueError(f"No captured piece of type {name} available to place")

        player.captured_pieces[name] -= 1
        self.pieces[position] = LightPiece(name, team, False, False, True)
        self.history.append(("place", team, name, position))

    def undo_action(self):
        if not self.history:
            raise ValueError("No actions to undo")

        last_action = self.history.pop()
        action_type = last_action[0]

        if action_type == "move":
            _, team, from_pos, to_pos, captured_piece, was_promoted, was_first_move = last_action
            piece = self.pieces[to_pos]

            # Undo move
            self.pieces[from_pos] = self.pieces.pop(to_pos)
            if captured_piece:
                self.pieces[to_pos] = captured_piece
                player = self.get_player(team)
                player.captured_pieces[captured_piece.name] -= 1

            # Undo promotion
            if was_promoted != piece.is_promoted:
                piece.demote()

            # Restore first move status
            piece.is_first_move = was_first_move

        elif action_type == "place":
            _, team, name, position = last_action
            del self.pieces[position]
            player = self.get_player(team)
            player.captured_pieces[name] += 1
