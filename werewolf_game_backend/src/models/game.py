from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    max_players = db.Column(db.Integer, default=10)
    current_players = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='waiting')  # waiting, in_progress, finished
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    game_state = db.Column(db.Text)  # JSON string for game state
    
    def __repr__(self):
        return f'<Game {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_code': self.room_code,
            'name': self.name,
            'max_players': self.max_players,
            'current_players': self.current_players,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_game_state(self):
        if self.game_state:
            import json
            return json.loads(self.game_state)
        return {}
    
    def set_game_state(self, state):
        import json
        self.game_state = json.dumps(state)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20))  # villager, werewolf, seer, witch, hunter
    is_alive = db.Column(db.Boolean, default=True)
    is_ready = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Player {self.player_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'player_name': self.player_name,
            'role': self.role,
            'is_alive': self.is_alive,
            'is_ready': self.is_ready,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

