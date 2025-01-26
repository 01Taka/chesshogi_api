from models.ai.light import LightBoard, LightPlayer
from models.game.game import Game
from models.piece.piece import Piece
from models.piece.pieces_info import PIECE_CLASSES, PIECE_VALUES, POSITION_SCORES_SETTING

class AIPlayer:
    POSITIVE_TEAM = "white"
    NEGATIVE_TEAM = "black"
    PROMOTE_LINE = 3

    @staticmethod
    def take_action(game: Game, depth: int=3):
        try:
            # AIによる最適なアクションを決定
            white_player = LightPlayer(game.white)
            black_player = LightPlayer(game.black)
            board = LightBoard(game.board, white_player, black_player)
            action, _ = AIPlayer.find_best_move(board, game.current_player.team, depth)

            # アクションの適用
            target_piece = game.board.pieces.get(action["from"])
            target_position = action.get("to")

            if not target_piece or not target_position:
                print("AIの動作が失敗しました: 有効なターゲットピースまたはターゲット位置が見つかりません")
                return None

            # ゲームアクションを実行
            game.perform_action(
                target_piece.piece_id, 
                action["promote"], 
                "move", 
                target_position[0], 
                target_position[1]
            )

            return {
                "pieceId": target_piece.piece_id,
                "from": action["from"],
                "to": action["to"],
                "promote": action["promote"],
            }

        except ValueError as e:
            print(f"AIアクションの実行中にエラーが発生しました: {e}")
            return None


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
            score += AIPlayer.get_position_scores(piece.name, position, piece.team, board.board_size)

        # Evaluate captured pieces
        for team, multiplier in [(AIPlayer.POSITIVE_TEAM, 1), (AIPlayer.NEGATIVE_TEAM, -1)]:
            player = board.get_player(team)
            for piece_name, count in player.captured_pieces.items():
                score += multiplier * PIECE_VALUES[piece_name] * count

        return score

    @staticmethod
    def get_possible_moves(board: LightBoard, team: str):
        """
        Get all possible moves for the given team, including promotion moves.

        Args:
            board (LightBoard): The current board state
            team (str): The team for which to get possible moves

        Returns:
            list[dict]: A list of possible moves in the format {"from": position, "to": position, "promote": bool}.
        """
        possible_moves = []

        for from_pos, piece in board.pieces.items():
            if piece.team == team:
                PieceClass: Piece = PIECE_CLASSES[piece.name]
                legal_moves = PieceClass.get_legal_moves_static(
                    from_pos, piece.team, piece.is_promoted, board.board_size, board.pieces, piece.is_first_move, piece.is_rearranged 
                )

                for to_pos in legal_moves:
                    # Add normal move
                    possible_moves.append({"from": from_pos, "to": to_pos, "promote": False})

                    # Check if promotion is possible
                    if PieceClass.can_promote_static(piece.team, from_pos[1], to_pos[1], board.board_size, AIPlayer.PROMOTE_LINE):
                        possible_moves.append({"from": from_pos, "to": to_pos, "promote": True})

        return possible_moves

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
            possible_moves = AIPlayer.get_possible_moves(board, maximizing_team)

            for move in possible_moves:
                # Perform the move with optional promotion
                board.move(maximizing_team, move["from"], move["to"], promote=move["promote"])
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
            possible_moves = AIPlayer.get_possible_moves(board, maximizing_team)

            for move in possible_moves:
                # Perform the move with optional promotion
                board.move(maximizing_team, move["from"], move["to"], promote=move["promote"])
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
