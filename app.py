from flask import Flask
from flask_cors import CORS
from routes.game_routes import game_routes

app = Flask(__name__)

# CORSを有効化
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(game_routes)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
