import logging
from flask import Blueprint, request, jsonify, json
from models.game.game import Game
from models.game.board import Board
from models.game.player import Player
from models.ai.ai_player import AIPlayer
from models.redis_client import get_redis_client

# ログ設定（必要に応じて設定を変更）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

game_routes = Blueprint("game_routes", __name__)

# データ保存 (14日間 = 14 * 24 * 60 * 60秒)
TTL_IN_SECONDS = 14 * 24 * 60 * 60

def validate_initialize_data(data: dict) -> None:
    """ゲーム初期化用の入力データのバリデーション"""
    required_keys = ["userId", "boardType", "black", "white"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"'{key}' is required in the request data.")

    # プレイヤーデータの必須項目チェック
    for team in ["black", "white"]:
        if "name" not in data[team]:
            raise ValueError(f"'name' is required for {team} player.")
        if team == "black":
            if "boardType" not in data[team] or "piecePlaceable" not in data[team]:
                raise ValueError(f"'boardType' and 'piecePlaceable' are required for black player.")
        elif team == "white":
            if "boardType" not in data[team] or "piecePlaceable" not in data[team]:
                raise ValueError(f"'boardType' and 'piecePlaceable' are required for white player.")

@game_routes.route("/initialize", methods=["POST"])
def initialize_game():
    """
    ゲームを初期化します。
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No input data provided."}), 400

        validate_initialize_data(data)
        user_id = data["userId"]

        # プレイヤーとボードを作成
        black = Player(player_id=data["black"]["name"], team="black")
        white = Player(player_id=data["white"]["name"], team="white")
        board = Board(
            board_type=data["boardType"],
            black_board=data["black"]["boardType"],
            white_board=data["white"]["boardType"],
            black_placeable=data["black"]["piecePlaceable"],
            white_placable=data["white"]["piecePlaceable"],
        )

        # ゲームオブジェクトを作成
        game = Game(black=black, white=white, board=board)

        # ゲーム状態を保存 (Redisまたはデータベース)
        game_data = json.dumps(game.to_dict())
        get_redis_client().set(f"game_cls_dict:{user_id}", game_data, ex=TTL_IN_SECONDS)

        logger.info(f"Game initialized for user_id: {user_id}")
        return jsonify({"message": "Game initialized successfully.", "userId": user_id}), 200

    except ValueError as ve:
        logger.error(f"Validation error during game initialization: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.exception("Unexpected error during game initialization")
        return jsonify({"error": "Internal server error."}), 500

@game_routes.route("/state/<user_id>", methods=["GET"])
def get_game_instance(user_id):
    """
    指定されたユーザーのゲーム状態を返します。
    """
    try:
        redis_client = get_redis_client()
        game_state_json = redis_client.get(f"game_cls_dict:{user_id}")

        if not game_state_json:
            return jsonify({"error": "Game not initialized."}), 400

        game_cls_dict = json.loads(game_state_json)
        game_instance = Game.from_dict(game_cls_dict)
        return jsonify(game_instance.get_game_data_dict()), 200

    except Exception as e:
        logger.exception(f"Unexpected error retrieving game state for user_id: {user_id}")
        return jsonify({"error": "Internal server error."}), 500

@game_routes.route("/action", methods=["POST"])
def perform_action():
    """
    プレイヤーのアクションを受け付け、ゲーム状態を更新します。
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No input data provided."}), 400

        # 必須パラメータのチェック
        required_params = ["userId", "targetPieceId", "actionType", "promote", "x", "y", "isAIResponds"]
        for param in required_params:
            if param not in data:
                raise ValueError(f"'{param}' is required in the request data.")

        user_id = data["userId"]
        redis_client = get_redis_client()
        game_state_json = redis_client.get(f"game_cls_dict:{user_id}")

        if not game_state_json:
            return jsonify({"error": "Game not initialized."}), 400

        game_cls_dict = json.loads(game_state_json)

        # アクションの実行
        game = Game.from_dict(game_cls_dict)
        try:
            game.perform_action(
                target_piece_id=data["targetPieceId"],
                action_type=data["actionType"],
                promote=data["promote"],
                x=data["x"],
                y=data["y"],
            )
        except ValueError as ve:
            logger.error(f"Error during perform_action: {ve}")
            return jsonify({"error": str(ve)}), 400

        # AIの行動
        ai_action = None
        if data.get("isAIResponds"):
            try:
                ai_depth = data.get("depth", 1)  # depthが指定されていなければデフォルト値を使用
                ai_action = AIPlayer.take_action(game, ai_depth)
            except Exception as ai_e:
                logger.exception("Error during AI action")
                # AIのエラーはゲーム自体への影響がないので、ログ出力にとどめる
                ai_action = {"error": "AI failed to take action."}

        # 状態を更新
        updated_game_data = json.dumps(game.to_dict())
        redis_client.set(f"game_cls_dict:{user_id}", updated_game_data, ex=TTL_IN_SECONDS)
        redis_client.expire(f"game_cls_dict:{user_id}", TTL_IN_SECONDS)

        return jsonify({
            "aiAction": ai_action,
            "gameState": game.get_game_data_dict()
        }), 200

    except ValueError as ve:
        logger.error(f"Validation error in perform_action: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.exception("Unexpected error during perform_action")
        return jsonify({"error": "Internal server error."}), 500
