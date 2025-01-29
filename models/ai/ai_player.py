from models.ai.light import LightBoard, LightPlayer
from models.piece.piece import Piece
from models.piece.pieces_info import PIECE_CLASSES, PIECE_VALUES, POSITION_SCORES_SETTING
import random

class AIPlayer:
    POSITIVE_TEAM = "white"
    NEGATIVE_TEAM = "black"
    PROMOTE_LINE = 3

    @staticmethod
    def take_action(game, depth: int=3):
        try:
            white_player = LightPlayer(game.white)
            black_player = LightPlayer(game.black)
            board = LightBoard(game, white_player, black_player)

            # AIによる最適なアクションを決定
            if depth > 0:
                action, _ = AIPlayer.find_best_move(board, game.current_player.team, depth)
            else:
                action = AIPlayer.get_random_action(board, game.current_player.team)

            if not action:
                print("詰みです")
                return None
            
            # アクションの適用
            action_type = action["type"]
            if action_type == "move":
                target_piece = game.board.pieces.get(action["from"])
                target_position = action["to"]
                from_pos = action["from"]
                promote = action["promote"]
            elif action_type == "place":
                player = game.black if action["team"] == "black" else game.white
                target_piece = player.get_captured_piece_by_name(action["name"])
                target_position = action["position"]
                from_pos = None
                promote = False
                
            if not target_piece or not target_position:
                print("AIの動作が失敗しました: 有効なターゲットピースまたはターゲット位置が見つかりません")
                return None

            # ゲームアクションを実行
            game.perform_action(
                target_piece.piece_id, 
                promote, 
                action_type, 
                target_position[0], 
                target_position[1]
            )

            return {
                "pieceId": target_piece.piece_id,
                "from": from_pos,
                "to": target_position,
                "promote": promote,
            }

        except ValueError as e:
            print(f"AIアクションの実行中にエラーが発生しました: {e}")
            return None
        
    @staticmethod
    def get_random_action(board, team):
        moves = AIPlayer.get_possible_moves(board, team, 0)
        return random.choice(moves)

    @staticmethod
    def get_position_scores(name, position, team, board_size, rate=1):
        # 名前から行と列の設定を取得
        row, col = POSITION_SCORES_SETTING[name]["row"], POSITION_SCORES_SETTING[name]["col"]
        
        # チームに応じたセンターのマルチプライヤ
        center_multiplier = -1 if team == AIPlayer.POSITIVE_TEAM else 1
        
        # 指定された位置のスコアを直接計算
        center = (board_size - 1) / 2
        row_score = (center - position[1]) * row
        col_score = abs((center - position[0]) * col) * center_multiplier
        
        # 最終的なスコアを返す
        return (row_score + col_score) * rate


    @staticmethod
    def calculate_current_score(board: LightBoard) -> int:
        """
        Calculate the current evaluation score for the board state.

        Args:
            board (LightBoard): The current board state

        Returns:
            int: The evaluation score, positive for POSITIVE_TEAM advantage, negative for NEGATIVE_TEAM advantage.
        """
        score = 0

        # Evaluate on-board pieces
        for position, piece in board.pieces.items():
            score += piece.value if piece.team == AIPlayer.POSITIVE_TEAM else -piece.value
            score += AIPlayer.get_position_scores(piece.name, position, piece.team, board.board_size, 0.3)

        # Evaluate captured pieces
        for team, multiplier in [(AIPlayer.POSITIVE_TEAM, 1), (AIPlayer.NEGATIVE_TEAM, -1)]:
            player = board.get_player(team)
            for piece_name, count in player.captured_pieces.items():
                score += multiplier * PIECE_VALUES[piece_name] * count

        return score

    @staticmethod
    def get_move_data(board: LightBoard, team):
        """
        Collects all possible moves for the given team and tracks enemy moves.
        
        Args:
            board (LightBoard): The current board state.
            team (str): The team to collect moves for.
        
        Returns:
            tuple: (possible_moves, enemy_moves, king_pos)
        """
        king_pos = None
        possible_moves = []
        enemy_moves = []

        for from_pos, piece in board.pieces.items():
            PieceClass: Piece = PIECE_CLASSES[piece.name]
            legal_moves, ally_blocks = PieceClass.get_legal_moves_static(
                from_pos, piece.team, piece.is_promoted, board.board_size, 
                board.pieces, piece.is_first_move, piece.is_rearranged
            )

            if piece.team == team:
                if piece.name in {"ShogiKing", "ChessKing"}:
                    king_pos = from_pos
                
                possible_moves.extend(
                    {"type": "move", "name": piece.name, "from": from_pos, "to": to_pos, "promote": promote}
                    for to_pos in legal_moves
                    for promote in ([False, True] if PieceClass.can_promote_static(piece.team, from_pos[1], to_pos[1], board.board_size, AIPlayer.PROMOTE_LINE) else [False])
                )
            else:
                enemy_moves.append({
                    "position": from_pos,
                    "moves": [*legal_moves, *ally_blocks],
                    "move_type": Piece.get_piece_move_type_by_name(piece.name)
                })
        
        return possible_moves, enemy_moves, king_pos

    @staticmethod
    def get_legal_places(board: LightBoard, team):
        """
        Get all possible piece placement moves for the given team.

        Args:
            board (LightBoard): The current board state.
            team (str): The team to get legal placements for.

        Returns:
            list[dict]: List of legal placement moves.
        """
        player = board.black_player if team == "black" else board.white_player
        return [
            {"type": "place", "team": team, "name": piece_name, "position": position}
            for piece_name, remaining in player.captured_pieces.items() if remaining >= 1 and board.placeable_state[piece_name]
            for position in PIECE_CLASSES[piece_name].get_legal_places_static(
                team, board.board_size, board.pieces, board.immobile_rows.get(piece_name)
            )
        ]

    @staticmethod
    def get_possible_moves(board: LightBoard, team: str, depth: int):
        """
        Get all possible moves for the given team, including promotion moves.

        Args:
            board (LightBoard): The current board state.
            team (str): The team for which to get possible moves.
            depth (int): Search depth (affects legal placements).

        Returns:
            list[dict]: A list of possible moves.
        """
        possible_moves, enemy_moves, king_pos = AIPlayer.get_move_data(board, team)
        
        if depth != 1:
            possible_moves.extend(AIPlayer.get_legal_places(board, team))

        if not king_pos:
            return possible_moves  # No king found (shouldn't happen in a valid game)

        try:
            king_movables, other_piece_movables, state = Piece.find_moves_to_escape_check(king_pos, enemy_moves, board.board_size)
        except:
                print("error")
                import traceback
                traceback.print_exc()

        if state == "checkmate":
            print("checkmate")
            return []
        if state == "check":
            possible_moves = [
                move for move in possible_moves
                if (move["name"] in {"ShogiKing", "ChessKing"} and move["type"] == "move" and move["to"] in king_movables) 
                or (move["type"] == "move" and move["to"] in other_piece_movables)
                or (move["type"] == "place" and move["position"] in other_piece_movables)
            ]

        return possible_moves

    @staticmethod
    def perform_move(move, board: LightBoard, maximizing_team):
        if move["type"] == "move":
            board.move(maximizing_team, move["from"], move["to"], promote=move["promote"])
        elif move["type"] == "place":
            board.place(move["team"], move["name"], move["position"])
        else:
            raise ValueError("行動タイプには move か place を指定してください。", move["type"])
            
    @staticmethod
    def find_best_move(board: LightBoard, maximizing_team: str, depth: int, alpha: float = float('-inf'), beta: float = float('inf')) -> tuple[dict, int]:
        """
        Find the best move using the minimax algorithm with alpha-beta pruning.

        Args:
            board (LightBoard): The current board state
            maximizing_team (str): The team maximizing the score ("white" or "black")
            depth (int): The depth of the minimax search
            alpha (float): The best score that the maximizing player can guarantee
            beta (float): The best score that the minimizing player can guarantee

        Returns:
            tuple[dict, int]: The best move and its evaluation score
        """
        if depth == 0:
            return None, AIPlayer.calculate_current_score(board)

        best_move = None
        if maximizing_team == AIPlayer.POSITIVE_TEAM:
            best_score = float('-inf')
            possible_moves = AIPlayer.get_possible_moves(board, maximizing_team, depth)

            for move in possible_moves:
                # Perform the move with optional promotion
                AIPlayer.perform_move(move, board, maximizing_team)

                _, score = AIPlayer.find_best_move(board, AIPlayer.NEGATIVE_TEAM, depth - 1, alpha, beta)
                board.undo_action()

                # Update the best move and score
                if score > best_score:
                    best_score, best_move = score, move
                alpha = max(alpha, best_score)

                # Alpha-beta pruning
                if beta <= alpha:
                    break

        else:
            best_score = float('inf')
            possible_moves = AIPlayer.get_possible_moves(board, maximizing_team, depth)

            for move in possible_moves:
                # Perform the move with optional promotion
                AIPlayer.perform_move(move, board, maximizing_team)

                _, score = AIPlayer.find_best_move(board, AIPlayer.POSITIVE_TEAM, depth - 1, alpha, beta)
                board.undo_action()

                # Update the best move and score
                if score < best_score:
                    best_score, best_move = score, move
                beta = min(beta, best_score)

                # Alpha-beta pruning
                if beta <= alpha:
                    break

        return best_move, best_score
