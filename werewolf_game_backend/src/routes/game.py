from flask import Blueprint, request, jsonify
from src.models.game import db, Game, Player
from src.game_engine import game_engine
import random
import string

game_bp = Blueprint('game', __name__)

def generate_room_code():
    """Generate a unique 6-character room code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Game.query.filter_by(room_code=code).first():
            return code

@game_bp.route('/games', methods=['GET'])
def get_games():
    """Get list of all available games"""
    games = Game.query.filter_by(status='waiting').all()
    return jsonify([game.to_dict() for game in games])

@game_bp.route('/games', methods=['POST'])
def create_game():
    """Create a new game room"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Game name is required'}), 400
    
    room_code = generate_room_code()
    max_players = data.get('max_players', 10)
    
    game = Game(
        room_code=room_code,
        name=data['name'],
        max_players=max_players
    )
    
    db.session.add(game)
    db.session.commit()
    
    # Create game in engine
    game_engine.create_game(room_code, data['name'], max_players)
    
    return jsonify(game.to_dict()), 201

@game_bp.route('/games/<room_code>', methods=['GET'])
def get_game(room_code):
    """Get game details by room code"""
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    players = Player.query.filter_by(game_id=game.id).all()
    game_data = game.to_dict()
    game_data['players'] = [player.to_dict() for player in players]
    
    return jsonify(game_data)

@game_bp.route('/games/<room_code>/join', methods=['POST'])
def join_game(room_code):
    """Join a game room"""
    data = request.get_json()
    
    if not data or 'player_name' not in data:
        return jsonify({'error': 'Player name is required'}), 400
    
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.status != 'waiting':
        return jsonify({'error': 'Game is not accepting new players'}), 400
    
    if game.current_players >= game.max_players:
        return jsonify({'error': 'Game is full'}), 400
    
    # Check if player name already exists in this game
    existing_player = Player.query.filter_by(
        game_id=game.id, 
        player_name=data['player_name']
    ).first()
    
    if existing_player:
        return jsonify({'error': 'Player name already taken'}), 400
    
    player = Player(
        game_id=game.id,
        player_name=data['player_name']
    )
    
    game.current_players += 1
    
    db.session.add(player)
    db.session.commit()
    
    # Add player to game engine
    game_engine.add_player(room_code, data['player_name'])
    
    return jsonify(player.to_dict()), 201

@game_bp.route('/games/<room_code>/leave', methods=['POST'])
def leave_game(room_code):
    """Leave a game room"""
    data = request.get_json()
    
    if not data or 'player_name' not in data:
        return jsonify({'error': 'Player name is required'}), 400
    
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    player = Player.query.filter_by(
        game_id=game.id,
        player_name=data['player_name']
    ).first()
    
    if not player:
        return jsonify({'error': 'Player not found in this game'}), 404
    
    game.current_players -= 1
    
    db.session.delete(player)
    db.session.commit()
    
    return jsonify({'message': 'Left game successfully'})

@game_bp.route('/games/<room_code>/start', methods=['POST'])
def start_game(room_code):
    """Start the game with game engine"""
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Start game in engine
    success, message = game_engine.start_game(room_code)
    
    if success:
        game.status = 'in_progress'
        db.session.commit()
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400

@game_bp.route('/games/<room_code>/ready', methods=['POST'])
def toggle_ready(room_code):
    """Toggle player ready status"""
    data = request.get_json()
    
    if not data or 'player_name' not in data:
        return jsonify({'error': 'Player name is required'}), 400
    
    game = Game.query.filter_by(room_code=room_code).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    player = Player.query.filter_by(
        game_id=game.id,
        player_name=data['player_name']
    ).first()
    
    if not player:
        return jsonify({'error': 'Player not found in this game'}), 404
    
    player.is_ready = not player.is_ready
    db.session.commit()
    
    return jsonify(player.to_dict())

