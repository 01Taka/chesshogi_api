from models.shogi_pieces import (
    ShogiKing, ShogiRook, ShogiBishop, ShogiGold,
    ShogiSilver, ShogiKnight, ShogiLance, ShogiPawn,
    ShogiJumper, ShogiPhoenix
)
from models.chess_pieces import (
    ChessKing, ChessQueen, ChessRook, ChessBishop,
    ChessKnight, ChessPawn, ChessPillar, ChessWisp, ChessLance
)

# 駒クラスを名前でマッピング（将棋とチェスの両方対応）
PIECE_CLASSES = {
    # 将棋の駒
    "shogi_king": ShogiKing,
    "shogi_rook": ShogiRook,
    "shogi_bishop": ShogiBishop,
    "shogi_gold": ShogiGold,
    "shogi_silver": ShogiSilver,
    "shogi_knight": ShogiKnight,
    "shogi_lance": ShogiLance,
    "shogi_pawn": ShogiPawn,
    "shogi_jumper": ShogiJumper,
    "shogi_phoenix": ShogiPhoenix,

    # チェスの駒
    "chess_king": ChessKing,
    "chess_queen": ChessQueen,
    "chess_rook": ChessRook,
    "chess_bishop": ChessBishop,
    "chess_knight": ChessKnight,
    "chess_pawn": ChessPawn,
    "chess_pillar": ChessPillar,
    "chess_wisp": ChessWisp,
    "chess_lance": ChessLance
}

SHOGI_BOARD_SIZE = 9
CHESS_BOARD_SIZE = 8

SHOGI_BOARD_POSITIONS = {
    "shogi": {
        "shogi_king": [(4, 0)],
        "shogi_rook": [(1, 1)],
        "shogi_bishop": [(7, 1)],
        "shogi_gold": [(3, 0), (5, 0)],
        "shogi_silver": [(2, 0), (6, 0)],
        "shogi_knight": [(1, 0), (7, 0)],
        "shogi_lance": [(0, 0), (8, 0)],
        "shogi_pawn": [(x, 2) for x in range(SHOGI_BOARD_SIZE)],
    },
    "wideChess": {
        "chess_king": [(5, 0)],
        "chess_queen": [(3, 0)],
        "chess_rook": [(0, 0), (8, 0)],
        "chess_bishop": [(2, 0), (6, 0)],
        "chess_knight": [(1, 0), (7, 0)],
        "chess_pawn": [(x, 1) for x in range(SHOGI_BOARD_SIZE)],
    },
    "replaceShogi": {
        "chess_king": [(4, 0)],
        "chess_rook": [(1, 1)],
        "chess_bishop": [(7, 1)],
        "chess_pillar": [(3, 0), (5, 0)],
        "chess_wisp": [(2, 0), (6, 0)],
        "chess_knight": [(1, 0), (7, 0)],
        "chess_lance": [(0, 0), (8, 0)],
        "chess_pawn": [(x, 2) for x in range(SHOGI_BOARD_SIZE)],
    }
}

CHESS_BOARD_POSITIONS = {
    "chess": {
        "chess_king": [(4, 0)],
        "chess_queen": [(3, 0)],
        "chess_rook": [(0, 0), (7, 0)],
        "chess_bishop": [(2, 0), (5, 0)],
        "chess_knight": [(1, 0), (6, 0)],
        "chess_pawn": [(x, 1) for x in range(CHESS_BOARD_SIZE)],
    },
    "narrowShogi": {
        "shogi_king": [(4, 0)],
        "shogi_rook": [(1, 1)],
        "shogi_bishop": [(6, 1)],
        "shogi_gold": [(3, 0), (5, 0)],
        "shogi_silver": [(2, 0), (6, 0)],
        "shogi_knight": [(1, 0)],
        "shogi_lance": [(0, 0), (7, 0)],
        "shogi_pawn": [(x, 2) for x in range(CHESS_BOARD_SIZE)],
    },
    "replaceChess": {
        "shogi_king": [(4, 0)],
        "shogi_phoenix": [(3, 0)],
        "shogi_rook": [(0, 0), (7, 0)],
        "shogi_bishop": [(2, 0), (5, 0)],
        "shogi_jumper": [(1, 0), (6, 0)],
        "shogi_pawn": [(x, 1) for x in range(CHESS_BOARD_SIZE)],
    }
}

PROMOTE_LINE = {
    "shogi": 3,
    "wideChess": 1,
    "replaceShogi": 1,
    "chess": 1,
    "narrowShogi": 2,
    "replaceChess": 2
}

class BoardInitializer:
    @staticmethod
    def get_id(n: int) -> str:
        """
        数値を文字列 (a, b, ..., aa, ab, ..., zz) に変換
        """
        result = []
        while n >= 0:
            result.append(chr(n % 26 + ord('a')))
            n = n // 26 - 1
        return ''.join(reversed(result))

    @staticmethod
    def initialize_pieces(
        positions: dict, 
        team: str, 
        board_size: int, 
        promote_line: int, 
        placeable: bool,
        start_id: int
    ) -> dict:
        """
        指定されたチームの駒を初期化して返す
        """
        pieces = {}
        piece_id = start_id

        for piece_name, piece_positions in positions.items():
            piece_class = PIECE_CLASSES[piece_name]
            for pos in piece_positions:
                piece = piece_class(
                    piece_id=BoardInitializer.get_id(piece_id),
                    position=pos,
                    team=team,
                    board_size=board_size,
                    promote_line=promote_line,
                    is_banned_place= not placeable
                )
                pieces[pos] = piece
                piece_id += 1

        return pieces, piece_id
    
    @staticmethod
    def reverse_positions(positions: dict, board_size, reverse_type):
        def reverse_position_list(position_list):
            new_position_list = []

            for x, y in position_list:
                if reverse_type == "point":
                    # 点対称の反転 (原点を中心に反転)
                    new_x = board_size - x - 1
                    new_y = board_size - y - 1
                elif reverse_type == "vertical":
                    new_x = x
                    new_y = board_size - y - 1
                else:
                    raise ValueError("Invalid reverse_type")
                
                new_position_list.append((new_x, new_y))
            
            return new_position_list
        
        new_positions = {}

        for piece_name, piece_positions in positions.items():
            new_positions[piece_name] = reverse_position_list(piece_positions)

        return new_positions


    @staticmethod
    def get_board(board_type: str, black_board: str, white_board: str, black_placeable: bool, white_placable: bool) -> dict:
        """
        将棋またはチェスの初期盤面を作成
        """
        if board_type not in ("shogi", "chess"):
            raise ValueError(f"Unsupported board type: {board_type}")

        positions = SHOGI_BOARD_POSITIONS if board_type == "shogi" else CHESS_BOARD_POSITIONS
        board_size = SHOGI_BOARD_SIZE if board_type == "shogi" else CHESS_BOARD_SIZE
        reverse_type = "point" if board_type == "shogi" else "vertical"
 
        if black_board not in positions or white_board not in positions:
            raise ValueError (f"Unsupported player board type: {black_board}, ${white_board}")
        
        pieces = {}

        # 黒の駒を初期化
        black_pieces, next_id = BoardInitializer.initialize_pieces(
            positions=positions[black_board],
            team="black",
            board_size=board_size,
            promote_line=PROMOTE_LINE[black_board],
            placeable=black_placeable,
            start_id=0,
        )
        pieces.update(black_pieces)

        # 白の駒を初期化
        white_pieces, _ = BoardInitializer.initialize_pieces(
            positions=BoardInitializer.reverse_positions(positions[white_board], board_size, reverse_type),
            team="white",
            board_size=board_size,
            promote_line=PROMOTE_LINE[black_board],
            placeable=white_placable,
            start_id=next_id,
        )
        pieces.update(white_pieces)

        return board_size, pieces
