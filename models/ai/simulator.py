from models.game import Game

class Simulator:
    def __init__(self, game: Game):
        """
        シミュレータを初期化します。

        Args:
            game (Game): シミュレーション対象のゲームインスタンス
        """
        self.game = game

    def simulate_action(self, target_piece_id, promote, action_type, x, y):
        """
        指定されたアクションを仮想的に実行し、評価値を返す。

        Args:
            target_piece_id (int): 対象の駒ID
            promote (bool): プロモーションの有無
            action_type (str): "move" または "place"
            x (int): 移動先のX座標
            y (int): 移動先のY座標

        Returns:
            float: アクション後のゲーム状態の評価値
        """
        # 現在のゲーム状態を保存
        backup_state = self.game.to_dict()

        try:
            # 仮想的にアクションを実行
            self.game.action(target_piece_id, promote, action_type, x, y)
            # 新しいゲーム状態を評価
            score = self.evaluate_state()
        finally:
            # ゲーム状態を元に戻す
            restored_game = Game.from_dict(backup_state)
            self.game.__dict__.update(restored_game.__dict__)

        return score

    def evaluate_state(self):
        """
        現在のゲーム状態を評価してスコアを返す。

        Returns:
            float: ゲーム状態の評価値
        """
        score = 0
        for piece in self.game.board.pieces.values():
            if piece.team == self.game.current_player.team:
                score += piece.value  # 駒の価値を加算
            else:
                score -= piece.value  # 敵駒の価値を減算

        # その他の評価ロジック（例: キングの安全性、駒の位置など）を追加
        return score

    def simulate_possible_actions(self):
        """
        現在のプレイヤーが可能なすべてのアクションをシミュレーションし、
        アクションごとの評価値を返す。

        Returns:
            list[tuple[dict, float]]: アクションとその評価値のリスト
        """
        possible_moves = []
        for piece in self.game.current_player.captured_pieces:
            legal_moves = piece.get_legal_moves(self.game.board.pieces)
            for move in legal_moves:
                possible_moves.append({
                    "piece_id": piece.id,
                    "promote": False,
                    "action_type": "move",
                    "x": move[0],
                    "y": move[1]
                })
                # プロモーションが可能な場合も追加
                if piece.can_promote(move):
                    possible_moves.append({
                        "piece_id": piece.piece_id,
                        "promote": True,
                        "action_type": "move",
                        "x": move[0],
                        "y": move[1]
                    })

        evaluations = []
        for action in possible_moves:
            score = self.simulate_action(
                action["piece_id"],
                action["promote"],
                action["action_type"],
                action["x"],
                action["y"]
            )
            evaluations.append((action, score))

        return evaluations
