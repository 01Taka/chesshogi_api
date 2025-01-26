from flask import Blueprint, request, jsonify, json
from models.game.game import Game
from models.game.board import Board
from models.game.player import Player
from models.ai.ai_player import AIPlayer
from models.redis_client import get_redis_client

game_routes = Blueprint("game_routes", __name__)


# データ保存 (14日間 = 14 * 24 * 60 * 60秒)
TTL_IN_SECONDS = 14 * 24 * 60 * 60

@game_routes.route("/initialize", methods=["POST"])
def initialize_game():
    """
    ゲームを初期化します。
    """
    data = request.json
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

    print(len(json.dumps(game.to_dict())))
    # ゲーム状態を保存 (Redisまたはデータベース)
    get_redis_client().set(f"game_cls_dict:{user_id}", json.dumps(game.to_dict()), ex=TTL_IN_SECONDS)

    return jsonify({"message": "Game initialized successfully.", "userId": user_id}), 200


@game_routes.route("/state/<user_id>", methods=["GET"])
def get_game_instance(user_id):
    """
    指定されたユーザーのゲーム状態を返します。
    """
    game_cls_dict = get_redis_client().get(f"game_cls_dict:{user_id}")

    if not game_cls_dict:
        return jsonify({"error": "Game not initialized."}), 400

    game_cls_dict = json.loads(game_cls_dict)
    game_instance = Game.from_dict(game_cls_dict)
    return jsonify(game_instance.get_game_data_dict()), 200


@game_routes.route("/action", methods=["POST"])
def perform_action():
    """
    プレイヤーのアクションを受け付け、ゲーム状態を更新します。
    """
    data = request.json
    user_id = data["userId"]

    # 現在のゲーム状態を取得
    game_state_json = get_redis_client().get(f"game_cls_dict:{user_id}")
    if not game_state_json:
        return jsonify({"error": "Game not initialized."}), 400

    game_cls_dict = json.loads(game_state_json)

    try:
        # アクションを実行
        # 仮想的に `Game` クラスのインスタンスでアクションを処理
        game = Game.from_dict(game_cls_dict)
        game.perform_action(
            target_piece_id=data["targetPieceId"],
            action_type=data["actionType"],
            promote=data["promote"],
            x=data["x"],
            y=data["y"],
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # AIの行動
    ai_action = None
    if data["isAIResponds"]:
        ai_action = AIPlayer.take_action(game)

    # 状態を更新
    get_redis_client().set(f"game_cls_dict:{user_id}", json.dumps(game.to_dict()), ex=TTL_IN_SECONDS)
    if data:
        get_redis_client().expire(f"game_cls_dict:{user_id}", TTL_IN_SECONDS)

    return jsonify({
        "aiAction": ai_action,
        "gameState": game.get_game_data_dict()
    }), 200
