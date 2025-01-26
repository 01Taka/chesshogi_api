from models.shogi_pieces import (
    ShogiKing, ShogiRook, ShogiBishop, ShogiGold,
    ShogiSilver, ShogiKnight, ShogiLance, ShogiPawn,
    ShogiJumper, ShogiPhoenix
)
from models.chess_pieces import (
    ChessKing, ChessQueen, ChessRook, ChessBishop,
    ChessKnight, ChessPawn, ChessPillar, ChessWisp, ChessLance
)

PIECE_CLASSES = {
    # 将棋の駒
    "ShogiKing": ShogiKing,
    "ShogiRook": ShogiRook,
    "ShogiBishop": ShogiBishop,
    "ShogiGold": ShogiGold,
    "ShogiSilver": ShogiSilver,
    "ShogiKnight": ShogiKnight,
    "ShogiLance": ShogiLance,
    "ShogiPawn": ShogiPawn,
    "ShogiJumper": ShogiJumper,
    "ShogiPhoenix": ShogiPhoenix,

    # チェスの駒
    "ChessKing": ChessKing,
    "ChessQueen": ChessQueen,
    "ChessRook": ChessRook,
    "ChessBishop": ChessBishop,
    "ChessKnight": ChessKnight,
    "ChessPawn": ChessPawn,
    "ChessPillar": ChessPillar,
    "ChessWisp": ChessWisp,
    "ChessLance": ChessLance
}

PIECE_VALUES = {
    # 将棋の駒
    "ShogiKing": 0,        # 王将は負けに直結するため評価関数で特別扱い
    "ShogiPawn": 1,
    "ShogiLance": 5,
    "ShogiKnight": 6,
    "ShogiSilver": 9,
    "ShogiGold": 10,
    "ShogiBishop": 13,
    "ShogiRook": 15,
    "ShogiJumper": 13,      
    "ShogiPhoenix": 27,    

    # チェスの駒
    "ChessKing": 0,        # キングは負けに直結するため特別扱い
    "ChessPawn": 3,
    "ChessKnight": 11,
    "ChessBishop": 11,
    "ChessRook": 14,
    "ChessQueen": 27,
    "ChessPillar": 10,      
    "ChessWisp": 9,        
    "ChessLance": 5,       
}

PROM_PIECE_VALUES = {
    # 将棋の駒
    "ShogiPawn": 10,
    "ShogiLance": 10,
    "ShogiKnight": 10,
    "ShogiSilver": 10,
    "ShogiBishop": 19,
    "ShogiRook": 21,
    "ShogiJumper": 16,     
    # 成れない駒はそのまま
    "ShogiKing": 0,        # 王将は昇格しない
    "ShogiPhoenix": 27,    

    # チェスの駒
    "ChessPawn": 23,        # ポーンの昇格先は通常クイーン
    "ChessLance": 11,      
    # 成れない駒はそのまま
    "ChessKing": 0,        # キングは昇格しない
    "ChessKnight": 11,
    "ChessBishop": 11,
    "ChessRook": 14,
    "ChessQueen": 27,
    "ChessPillar": 10,     
    "ChessWisp": 9,       
}
