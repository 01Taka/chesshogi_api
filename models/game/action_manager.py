import copy
from models.piece.chess_pieces import ChessKing, ChessRook, ChessPawn
from models.piece.piece import Piece
from models.game.board import Board
from models.game.player import Player

class ActionManager:

    @staticmethod
    def action(player: Player, board: Board, target_piece_id, promote, action_type, x, y):
        piece = ActionManager.get_target_piece(player, board, target_piece_id, action_type)
        
        # Validate action and piece state
        ActionManager.validate_piece_for_action(piece, player, action_type)

        if action_type == "move":
            prev_position_y = piece.position[1] if piece.position else None
            ActionManager.move_piece(player, board, piece, (x, y))
            if promote:
                piece.set_promote(True, prev_position_y)
        elif action_type == "place":
            ActionManager.place_piece(player, board, piece, (x, y))

        # Record the last move
        last_move = {
            "action_type": action_type,
            "piece_id": target_piece_id,
            "piece_name": piece.name,
            "team": player.team,
            "from": piece.position if action_type == "move" else None,
            "to": (x, y),
        }

        return last_move

    @staticmethod
    def get_target_piece(player: Player, board: Board, target_piece_id: str, action_type: str) -> Piece:
        """Returns the target piece based on the action type."""
        if action_type == "move":
            return board.get_piece_by_id(target_piece_id)
        elif action_type == "place":
            return player.get_captured_piece_by_id(target_piece_id)
        else:
            raise ValueError("Invalid action type")

    @staticmethod
    def validate_piece_for_action(piece: Piece, player: Player, action_type: str):
        """Validates the piece based on the action and player's team."""
        if not piece:
            raise ValueError("Piece with the given ID does not exist.")
        if piece.team != player.team:
            raise ValueError("The player's team does not match the piece's team.")
        if (piece.position and action_type == "place") or (not piece.position and action_type == "move"):
            raise ValueError("Invalid action: piece state does not match the action.")

    @staticmethod
    def move_piece(player: Player, board: Board, piece: Piece, new_position: tuple[int, int]):
        """Moves a piece on the board."""
        prev_position = copy.deepcopy(piece.position)
        special_processing_pieces = ActionManager.get_special_processing_pieces(piece, new_position, board.pieces)

        # コピーして移動処理が終わった後に使う
        captured_piece: Piece = copy.deepcopy(board.get_piece(new_position))

        piece.on_move(new_position, board.pieces)
        board.on_move_piece(piece, prev_position, new_position)

        if captured_piece and captured_piece.team != piece.team:
            ActionManager.capture_piece(player, captured_piece, piece.team)
        
        ActionManager.special_processing(player, board, prev_position, piece, special_processing_pieces)

    @staticmethod
    def place_piece(player: Player, board: Board, piece: Piece, position: tuple[int, int]):
        """Places a captured piece on the board."""
        if not piece.position and position and piece.can_place(position, board.pieces):
            if not board.get_piece(position):
                piece.on_place(position, board.pieces)
                board.on_place_piece(piece, position)
                player.on_place_piece(piece)
            else:
                raise ValueError("Position is already occupied.")
        else:
            raise ValueError("Invalid piece placement.")
        
    @staticmethod
    def get_special_processing_pieces(piece: Piece, new_position, pieces: dict):
        rook, en_passant_pawn = None, None

        if isinstance(piece, ChessKing):
            rook = ChessKing.get_castling_partner(piece.position, new_position, piece.team, piece.board_size, pieces)
        elif isinstance(piece, ChessPawn):
            en_passant_pawn = ChessPawn.get_en_passant_target(piece.team, new_position, pieces)

        return {
            "castling_rook": rook,
            "en_passant_pawn": en_passant_pawn
        }

    @staticmethod
    def special_processing(player: Player, board: Board, prev_position, piece, special_processing_pieces: dict):
        """Handles special chess cases like castling and en passant."""
        if isinstance(piece, ChessKing) and special_processing_pieces.get("castling_rook"):
            ActionManager.handle_castling(player, prev_position, special_processing_pieces["castling_rook"], board)
        elif isinstance(piece, ChessPawn) and special_processing_pieces.get("en_passant_pawn"):
            ActionManager.handle_en_passant(piece.team, special_processing_pieces["en_passant_pawn"], player, board)

    @staticmethod
    def handle_castling(player: Player, king_prev_position, castling_rook, board):
        """Handles castling for the ChessKing piece."""
        if castling_rook and isinstance(castling_rook, ChessRook):
            position = castling_rook.get_after_castling_position(king_prev_position)
            ActionManager.move_piece(player, board, castling_rook, position)

    @staticmethod
    def handle_en_passant(attack_team: ChessPawn, en_passant_pawn: ChessPawn, player, board: Board):
        """Handles en passant for the ChessPawn piece."""
        if en_passant_pawn and isinstance(en_passant_pawn, ChessPawn):
            board.on_capture_piece(en_passant_pawn.position)
            ActionManager.capture_piece(player, en_passant_pawn, attack_team)

    @staticmethod
    def capture_piece(player: Player, piece: Piece, capturing_team):
        """Captures a piece and adds it to the current player's captured pieces."""
        piece.on_captured(capturing_team)
        player.add_captured_piece(piece)

