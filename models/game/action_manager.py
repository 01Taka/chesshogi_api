import copy
from models.piece.chess_pieces import ChessKing, ChessRook, ChessPawn
from models.piece.piece import Piece
from models.game.board import Board
from models.game.player import Player
from models.type import Pieces, PiecePosition, LastMove

class ActionManager:

    @staticmethod
    def action(player: Player, board: Board, target_piece_id, promote, action_type, x, y, last_move: LastMove):
        piece = ActionManager.get_target_piece(player, board, target_piece_id, action_type)
        if not piece:
            raise ValueError(f"No pieces found. action type: {action_type}")

        from_position = Board.get_piece_position_by_id(piece.piece_id, board.pieces)
        is_placed = bool(from_position)

        to_position = (x, y)

        # Validate action and piece state
        ActionManager.validate_piece_for_action(is_placed, piece, player, action_type)

        if action_type == "move":
            ActionManager.move_piece(player, board, piece, from_position, to_position, last_move)
            if promote:
                piece.to_promote_with_verification(from_position[1], to_position[1])
        elif action_type == "place":
            ActionManager.place_piece(player, board, piece, to_position)
        
        # Record the last move
        last_move = {
            "action_type": action_type,
            "piece_id": target_piece_id,
            "piece_name": piece.name,
            "team": player.team,
            "from_pos": from_position if action_type == "move" else None,
            "to_pos": to_position,
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
            raise ValueError(f"Invalid action type. {action_type}")

    @staticmethod
    def validate_piece_for_action(is_placed, piece: Piece, player: Player, action_type: str):
        """Validates the piece based on the action and player's team."""
        if not piece:
            raise ValueError("Piece with the given ID does not exist.")
        if piece.team != player.team:
            raise ValueError("The player's team does not match the piece's team.")
        if (is_placed and action_type == "place") or (not is_placed and action_type == "move"):
            raise ValueError("Invalid action: piece state does not match the action.")

    @staticmethod
    def move_piece(player: Player, board: Board, piece: Piece, from_position: tuple[int, int], to_position: tuple[int, int], last_move: LastMove):
        """Moves a piece on the board."""
        special_processing_pieces = ActionManager.get_special_processing_pieces(piece, from_position, to_position, board.pieces, last_move)

        # コピーして移動処理が終わった後に使う
        captured_piece: Piece = copy.deepcopy(board.get_piece(to_position))

        piece.on_move_with_verification(from_position, to_position, board.pieces, last_move=last_move)
        board.on_move_piece(piece, from_position, to_position)

        if captured_piece and captured_piece.team != piece.team:
            ActionManager.capture_piece(player, captured_piece, piece.team)

        ActionManager.special_processing(player, board, from_position, piece, special_processing_pieces)


    @staticmethod
    def place_piece(player: Player, board: Board, piece: Piece, position: tuple[int, int]):
        """Places a captured piece on the board."""
        if Board.get_piece_position_by_id(piece.piece_id, board.pieces):
            raise ValueError("This piece is already in place.")
        
        if position and piece.can_place(position, board.pieces):
            if not board.get_piece(position):
                piece.on_place(position, board.pieces)
                board.on_place_piece(piece, position)
                player.on_place_piece(piece)
            else:
                raise ValueError("Position is already occupied.")
        else:
            raise ValueError("Invalid piece placement.")
        
    @staticmethod
    def get_special_processing_pieces(piece: Piece, from_position, to_position, pieces: Pieces, last_move: LastMove) -> dict[str, PiecePosition]:
        rook, en_passant_pawn = None, None

        if isinstance(piece, ChessKing):
            rook = ChessKing.get_castling_partner(from_position, to_position, piece.team, piece.board_size, pieces)
        elif isinstance(piece, ChessPawn):
            en_passant_pawn, position, _ = ChessPawn.get_en_passant(piece.team, from_position, pieces, last_move)

        return {
            "castling_rook": {
                "piece": rook,
                "position": Board.get_piece_position_by_id(rook.piece_id, pieces),
            } if rook else None,
            "en_passant_pawn": {
                "piece": en_passant_pawn,
                "position": position,
            } if en_passant_pawn else None,
        }

    @staticmethod
    def special_processing(player: Player, board: Board, prev_position, piece, special_processing_pieces: dict[str, PiecePosition]):
        """Handles special chess cases like castling and en passant."""
        castling_rook_move = special_processing_pieces.get("castling_rook")
        en_passant_pawn_move = special_processing_pieces.get("en_passant_pawn")

        if isinstance(piece, ChessKing) and castling_rook_move:
            ActionManager.handle_castling(castling_rook_move["piece"], castling_rook_move["position"], prev_position, board)
        elif isinstance(piece, ChessPawn) and en_passant_pawn_move:
            ActionManager.handle_en_passant(piece.team, en_passant_pawn_move["position"], en_passant_pawn_move["piece"], player, board)

    @staticmethod
    def handle_castling(castling_rook, rook_prev_position, king_prev_position, board: Board):
        """Handles castling for the ChessKing piece."""
        if castling_rook and isinstance(castling_rook, ChessRook):
            rook_to_position = castling_rook.get_after_castling_position(rook_prev_position, king_prev_position)
            castling_rook.on_move(rook_to_position)
            board.on_move_piece(castling_rook, rook_prev_position, rook_to_position)

    @staticmethod
    def handle_en_passant(attack_team: ChessPawn, from_position, en_passant_pawn: ChessPawn, player, board: Board):
        """Handles en passant for the ChessPawn piece."""
        if en_passant_pawn and isinstance(en_passant_pawn, ChessPawn):
            board.on_capture_piece(from_position)
            ActionManager.capture_piece(player, en_passant_pawn, attack_team)

    @staticmethod
    def capture_piece(player: Player, piece: Piece, capturing_team):
        """Captures a piece and adds it to the current player's captured pieces."""
        piece.on_captured(capturing_team)
        player.add_captured_piece(piece)

