from models.piece.piece import Piece
from models.game.board import Board
import copy

class Player:
    def __init__(self, player_id: str, team: str, captured_pieces: list[Piece] = []):
        self.__player_id = player_id
        self.__team = team
        self.__captured_pieces = captured_pieces

    def copy(self):
        return Player(self.player_id, self.team, copy.deepcopy(self.__captured_pieces))
    
    @property
    def player_id(self):
        return self.__player_id

    @property
    def team(self):
        return self.__team
    
    @team.setter
    def team(self, value):
        if value in ("black", "white"):
            self.__team = value
    
    @property
    def captured_pieces(self) -> list[Piece]:
        return list(self.__captured_pieces)
    
    @property
    def captured_piece_count(self):
        return len(self.__captured_pieces)

    def add_captured_piece(self, piece: Piece):
        self.__captured_pieces.append(piece)
        self.__captured_pieces.sort()

    def get_captured_piece_by_id(self, piece_id):
        return next((piece for piece in self.__captured_pieces if piece.piece_id == piece_id), None)
    
    def get_captured_piece_by_name(self, name):
        return next((piece for piece in self.__captured_pieces if piece.name == name), None)

    def on_place_piece(self, piece: Piece):
        self.__captured_pieces.remove(piece)

    def reset_captured_pieces(self):
        self.__captured_pieces.clear()

    def to_dict(self):
        return {
            "player_id": self.__player_id,
            "team": self.__team,
            "captured_pieces": [piece.to_dict() for piece in self.__captured_pieces],
        }
    
    @staticmethod
    def from_dict(data):
        player = Player(player_id=data["player_id"], team=data["team"])
        player.__captured_pieces = [Board.piece_from_dict(piece) for piece in data["captured_pieces"]]
        return player

    def __repr__(self):
        return f"Player(player_id={self.__player_id}, team={self.__team}, captured_pieces={len(self.__captured_pieces)})"
