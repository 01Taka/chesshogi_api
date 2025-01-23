from flask import Blueprint, request, jsonify
from models.game import Game
from models.board import Board
from models.player import Player
from models.send_data_manager import SendDataManager

game_routes = Blueprint("game_routes", __name__)

# グローバル変数でゲーム状態を保持
game_instance = None

@game_routes.route("/initialize", methods=["POST"])
def initialize_game():
    """
    ゲームを初期化します。
    フロントエンドからプレイヤー情報を受け取り、ゲームを開始します。
    """
    global game_instance
    data = request.json

    # プレイヤーとボードを作成
    black = Player(player_id=data["black"]["name"], team="black")
    white = Player(player_id=data["white"]["name"], team="white")

    board_type = data["boardType"]
    black_board, black_placeable = data["black"]["boardType"], data["black"]["piecePlaceable"]
    white_board, white_placeable = data["white"]["boardType"], data["white"]["piecePlaceable"]

    board = Board(board_type=board_type, black_board=black_board, white_board=white_board, black_placeable=black_placeable, white_placable=white_placeable)
    
    # ゲームを初期化
    game_instance = Game(black=black, white=white, board=board)

    board_settings = {
        "type": board_type,
        "size": board.size,
        "blackBoard": black_board,
        "whiteBoard": white_board
    }

    return jsonify({ "message": "Game initialized successfully.", "boardSettings": board_settings }), 200


@game_routes.route("/state", methods=["GET"])
def get_game_state():
    """
    現在のゲーム状態をJSON形式で返します。
    """
    if not game_instance:
        return jsonify({"error": "Game not initialized."}), 400
    
    board_settings = {
        "type": game_instance.board.board_type,
        "size": game_instance.board.size,
        "blackBoard": game_instance.board.board_type,
        "whiteBoard": game_instance.board.white_board
    }

    game_state = {
        "pieces": game_instance.board.pieces,
        "board_settings": board_settings,
        "board_size": board_settings["size"],
        "black_captured_pieces": game_instance.black.captured_pieces,
        "white_captured_pieces": game_instance.white.captured_pieces,
        "current_team": game_instance.current_player.team,
        "step": game_instance.step,
        "last_move": game_instance.last_move,
        "white_checked": False, # game_instance.white.checked,  # 仮に`checked`プロパティが存在する場合
        "black_checked": False, # game_instance.black.checked,  # 同上
        "game_result": None,  # ゲームの結果（引き分けなど）
        "error": None  # エラーメッセージ
    }

    return jsonify(SendDataManager.create_json(game_state)), 200


@game_routes.route("/action", methods=["POST"])
def perform_action():
    """
    プレイヤーのアクションを受け付け、ゲーム状態を更新します。
    """

    global game_instance
    if not game_instance:
        return jsonify({"error": "Game not initialized."}), 400

    data = request.json
    try:
        # アクション実行
        game_instance.action(
            target_piece_id=data["targetPieceId"],
            action_type=data["actionType"],
            promote=data["promote"],
            x=data["x"],
            y=data["y"]
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    return get_game_state()
