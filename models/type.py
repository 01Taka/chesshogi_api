from typing import NamedTuple, TypedDict

class PieceBase(NamedTuple):
    piece_id: str
    name: str
    team: str
    is_promoted: bool
    is_first_move: bool
    is_rearranged: bool

Pieces = dict[tuple[int, int], PieceBase]

class PiecePosition(TypedDict):
    piece: PieceBase
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]

class LastMove(TypedDict):
    action_type: str
    piece_id: str
    piece_name: str
    team: str
    from_pos: tuple[int, int] | None
    to_pos: tuple[int, int]