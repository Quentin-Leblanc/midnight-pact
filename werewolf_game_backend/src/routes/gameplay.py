from flask import Blueprint, request, jsonify
from src.game_engine import game_engine

gameplay_bp = Blueprint('gameplay', __name__)

@gameplay_bp.route('/games/<room_code>/start', methods=['POST'])
def start_game(room_code):
    """Start a game"""
    try:
        success, message = game_engine.start_game(room_code)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'game_state': game_engine.get_game_state(room_code)
            })
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/state', methods=['GET'])
def get_game_state(room_code):
    """Get current game state"""
    try:
        state = game_engine.get_game_state(room_code)
        
        if state:
            return jsonify(state)
        else:
            # Try to sync game from database if it exists but not in engine
            from src.models.game import Game, Player
            game = Game.query.filter_by(room_code=room_code).first()
            if game:
                # Create game in engine
                game_engine.create_game(room_code, game.name, game.max_players)
                # Add all players to engine
                players = Player.query.filter_by(game_id=game.id).all()
                for player in players:
                    game_engine.add_player(room_code, player.player_name)
                
                # Get state again
                state = game_engine.get_game_state(room_code)
                if state:
                    return jsonify(state)
            
            return jsonify({'error': 'Game not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/player/<player_name>/role', methods=['GET'])
def get_player_role(room_code, player_name):
    """Get player's role information"""
    try:
        role_info = game_engine.get_player_role(room_code, player_name)
        
        if role_info:
            return jsonify(role_info)
        else:
            # Try to sync game from database if it exists but not in engine
            from src.models.game import Game, Player
            game = Game.query.filter_by(room_code=room_code).first()
            if game:
                # Create game in engine if not exists
                if room_code not in game_engine.games:
                    game_engine.create_game(room_code, game.name, game.max_players)
                    # Add all players to engine
                    players = Player.query.filter_by(game_id=game.id).all()
                    for player in players:
                        game_engine.add_player(room_code, player.player_name)
                
                # Try to get role again
                role_info = game_engine.get_player_role(room_code, player_name)
                if role_info:
                    return jsonify(role_info)
            
            return jsonify({'error': 'Player not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/player/<player_name>/actions', methods=['GET'])
def get_available_actions(room_code, player_name):
    """Get available actions for a player"""
    try:
        actions = game_engine.get_available_actions(room_code, player_name)
        return jsonify({'actions': actions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/night-action', methods=['POST'])
def perform_night_action(room_code):
    """Perform a night action"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        action = data.get('action')
        target = data.get('target')
        
        success, message = game_engine.perform_night_action(room_code, player_name, action, target)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/vote', methods=['POST'])
def cast_vote(room_code):
    """Cast a vote during voting phase"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        target = data.get('target')
        
        success, message = game_engine.cast_vote(room_code, player_name, target)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/advance-phase', methods=['POST'])
def advance_phase(room_code):
    """Advance to the next phase (for testing/admin)"""
    try:
        success, message = game_engine.advance_phase(room_code)
        
        return jsonify({
            'success': success,
            'message': message,
            'game_state': game_engine.get_game_state(room_code)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/chat', methods=['POST'])
def send_chat_message(room_code):
    """Send a chat message"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        message = data.get('message')
        
        success, result = game_engine.add_chat_message(room_code, player_name, message)
        
        if success:
            return jsonify({
                'success': True,
                'message': result,
                'chat_messages': game_engine.get_game_state(room_code)['chat_messages']
            })
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/chat', methods=['GET'])
def get_chat_messages(room_code):
    """Get chat messages"""
    try:
        state = game_engine.get_game_state(room_code)
        
        if state:
            return jsonify({'chat_messages': state.get('chat_messages', [])})
        else:
            # Try to sync game from database if it exists but not in engine
            from src.models.game import Game, Player
            game = Game.query.filter_by(room_code=room_code).first()
            if game:
                # Create game in engine if not exists
                if room_code not in game_engine.games:
                    game_engine.create_game(room_code, game.name, game.max_players)
                    # Add all players to engine
                    players = Player.query.filter_by(game_id=game.id).all()
                    for player in players:
                        game_engine.add_player(room_code, player.player_name)
                
                # Return empty chat for now
                return jsonify({'chat_messages': []})
            
            return jsonify({'error': 'Game not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/history', methods=['GET'])
def get_game_history(room_code):
    """Get game history"""
    try:
        state = game_engine.get_game_state(room_code)
        
        if state:
            return jsonify({'game_history': state.get('game_history', [])})
        else:
            return jsonify({'error': 'Game not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/player/<player_name>/last-will', methods=['POST'])
def save_last_will(room_code, player_name):
    """Save player's last will"""
    try:
        data = request.get_json()
        last_will = data.get('last_will', '')
        
        success, message = game_engine.save_last_will(room_code, player_name, last_will)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

