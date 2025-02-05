from models.piece.piece import Piece
from models.piece.chess_pieces import ChessPawn
from models.type import PieceBase, LastMove

class SendDataManager:
    @staticmethod
    def create_board(pieces: dict[tuple[int, int], PieceBase], size: int) -> list[list[dict | None]]:
        board = []
        for y in range(size):
            row = []
            for x in range(size):
                piece: Piece = pieces.get((x, y))
                if piece:
                    data = {
                        "id": piece.piece_id,
                        "name": piece.name,
                        "promoted": piece.is_promoted,
                        "promotable": not piece.is_promoted and not piece.is_banned_promote,
                        "promoteLine": piece.promote_line,
                        "immobileRow": piece.immobile_row,
                        "rearranged": piece.is_rearranged,
                        "team": piece.team,
                    }
                    row.append(data)
                else:
                    row.append(None)
            board.append(row)
        return board

    @staticmethod
    def create_captured_pieces(black_captured_pieces: list[Piece], white_captured_pieces: list[Piece]) -> dict:
        def get_captured_pieces(captured_pieces: list[Piece]) -> dict:
            data = {}
            for piece in captured_pieces:
                if piece.name in data:
                    data[piece.name]["pieceIds"].append(piece.piece_id)
                else:
                    data[piece.name] = {
                        "pieceIds": [piece.piece_id],
                        "name": piece.name,
                        "placeable": not piece.is_banned_place
                    }
            return list(data.values())
        
        return {
            "black": get_captured_pieces(black_captured_pieces),
            "white": get_captured_pieces(white_captured_pieces)
        }

    @staticmethod
    def get_legal_moves_method(pieces: dict[tuple[int, int], Piece], last_move: LastMove):
        legals: dict[str, list] = {}
        ally_blocks: dict[str, list] = {}

        for position, piece in pieces.items():
            legals[piece.piece_id], ally_blocks[piece.piece_id] = piece.get_legal_moves(position, pieces, last_move)

        return legals, ally_blocks

    @staticmethod
    def get_legal_places(captured_pieces: list[Piece], pieces: dict[tuple[int, int], PieceBase], size: int) -> dict:
        legals = {}
        for piece in captured_pieces:
            legal_positions = []
            for x in range(size):
                for y in range(size):
                    if piece.can_place((x, y), pieces):
                        legal_positions.append((x, y))
            legals[piece.piece_id] = legal_positions
        return legals

    @staticmethod
    def create_legal_actions(pieces: dict[tuple[int, int], Piece], last_move: LastMove, captured_pieces: list[Piece], size: int) -> dict:
        legal_moves, ally_blocks = SendDataManager.get_legal_moves_method(pieces, last_move)
        legal_places = SendDataManager.get_legal_places(captured_pieces, pieces, size)
        actions = {}
        for piece in [*pieces.values(), *captured_pieces]:
            actions[piece.piece_id] = {
                "team": piece.team,
                "allyBlocks": ally_blocks.get(piece.piece_id, []),
                "moves": legal_moves.get(piece.piece_id, []),
                "places": legal_places.get(piece.piece_id, [])
            }
        return actions

    @staticmethod
    def create_game_data_dict(game_state: dict) -> dict:
        return {
            "board": SendDataManager.create_board(game_state["pieces"], game_state["board_size"]),
            "boardSettings": game_state["board_settings"],
            "capturedPieces": SendDataManager.create_captured_pieces(
                game_state["black_captured_pieces"], game_state["white_captured_pieces"]
            ),
            "legalActions": SendDataManager.create_legal_actions(
                game_state["pieces"],
                game_state["last_move"], 
                [*game_state["black_captured_pieces"], *game_state["white_captured_pieces"]], 
                game_state["board_size"]
            ),
            "turn": {
                "player": game_state["current_team"],
                "step": game_state["step"]
            },
            "lastMove": game_state.get("last_move"),
            "checkStatus": {
                "white": game_state["white_checked"],
                "black": game_state["black_checked"],
            },
            "gameResult": game_state.get("game_result"),
            "error": game_state.get("error")
        }
