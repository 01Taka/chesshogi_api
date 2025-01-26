from models.piece.piece import Piece

def hash_board(pieces, size, black_captured_pieces, white_captured_pieces):
    """
    Generates a unique hash string representing the board state.
    """
    def serialize_board_state():
        state = []
        for y in range(1, size + 1):
            for x in range(1, size + 1):
                piece: Piece = pieces.get((x, y))
                if piece:
                    promote_state = "P" if piece.is_promoted else "N"
                    state.append(f"{x}_{y}_{piece.name}_{piece.team}_{promote_state}")
                else:
                    state.append(f"{x}_{y}_._._.")
        return state

    def serialize_captured_pieces(captured_pieces: list[Piece]):
        counts = {}
        for piece in captured_pieces:
            key = f"{piece.name}_{piece.team}"
            counts[key] = counts.get(key, 0) + 1
        return [f"{key}_x{count}" for key, count in counts.items()]

    # Serialize board state
    data = serialize_board_state()
    data.append("/")

    # Serialize captured pieces
    data.extend(serialize_captured_pieces(black_captured_pieces))
    data.append("/")
    data.extend(serialize_captured_pieces(white_captured_pieces))

    return ",".join(data)
