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
    """Send a chat message (legacy endpoint - uses public channel)"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        message = data.get('message')
        
        # Use public channel by default for backward compatibility
        from src.game_engine import ChatChannel
        success, result = game_engine.add_chat_message(room_code, player_name, message, ChatChannel.PUBLIC)
        
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

@gameplay_bp.route('/games/<room_code>/trial-vote', methods=['POST'])
def cast_trial_vote(room_code):
    """Cast a trial vote (innocent/guilty)"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        verdict = data.get('verdict')  # 'innocent' or 'guilty'
        
        # Convert string to enum
        from src.game_engine import TrialVerdict
        if verdict == 'guilty':
            verdict_enum = TrialVerdict.GUILTY
        elif verdict == 'innocent':
            verdict_enum = TrialVerdict.INNOCENT
        else:
            return jsonify({'success': False, 'error': 'Invalid verdict'}), 400
        
        success, message = game_engine.cast_trial_vote(room_code, player_name, verdict_enum)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/trial-info', methods=['GET'])
def get_trial_info(room_code):
    """Get trial information"""
    try:
        state = game_engine.get_game_state(room_code)
        
        if state and state.get('phase') == 'trial':
            from src.game_engine import game_engine as ge
            game = ge.games.get(room_code)
            if game:
                return jsonify({
                    'accused_player': game.get('accused_player'),
                    'trial_defense_time': game.get('trial_defense_time', 30),
                    'trial_voting_time': game.get('trial_voting_time', 30),
                    'trial_votes': game.get('trial_votes', {}),
                    'trial_history': game.get('trial_history', [])
                })
        
        return jsonify({'error': 'No trial in progress'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/chat-channels', methods=['GET'])
def get_chat_channels(room_code):
    """Get available chat channels for a player"""
    try:
        player_name = request.args.get('player_name')
        if not player_name:
            return jsonify({'error': 'player_name required'}), 400
            
        channels = game_engine.get_available_chat_channels(room_code, player_name)
        return jsonify({'channels': channels})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/chat-messages', methods=['GET'])
def get_all_chat_messages(room_code):
    """Get all accessible chat messages for a player"""
    try:
        player_name = request.args.get('player_name')
        if not player_name:
            return jsonify({'error': 'player_name required'}), 400
            
        messages = game_engine.get_chat_messages(room_code, player_name)
        return jsonify({'messages': messages})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/chat/<channel>', methods=['POST'])
def send_channel_message(room_code, channel):
    """Send message to specific chat channel"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        message = data.get('message')
        
        if not player_name or not message:
            return jsonify({'error': 'player_name and message required'}), 400
        
        # Convert channel string to enum
        from src.game_engine import ChatChannel
        channel_enum = None
        
        if channel == 'public':
            channel_enum = ChatChannel.PUBLIC
        elif channel == 'mafia':
            channel_enum = ChatChannel.MAFIA
        elif channel == 'triad':
            channel_enum = ChatChannel.TRIAD
        elif channel == 'dead':
            channel_enum = ChatChannel.DEAD
        elif channel == 'private':
            channel_enum = ChatChannel.PRIVATE
        else:
            return jsonify({'error': 'Invalid channel'}), 400
        
        success, result = game_engine.add_chat_message(room_code, player_name, message, channel_enum)
        
        if success:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/private-message', methods=['POST'])
def send_private_message_route(room_code):
    """Send private message with public notification"""
    try:
        data = request.get_json()
        sender = data.get('sender')
        recipient = data.get('recipient')
        message = data.get('message')
        
        if not sender or not recipient or not message:
            return jsonify({'error': 'sender, recipient and message required'}), 400
        
        success, result = game_engine.send_private_message(room_code, sender, recipient, message)
        
        if success:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'error': result}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 🆕 ==================== ROUTES TESTAMENT & NOTES DE MORT ====================

@gameplay_bp.route('/games/<room_code>/player/<player_name>/will', methods=['GET'])
def get_player_will_route(room_code, player_name):
    """Get player's last will"""
    try:
        will_data = game_engine.get_player_will(room_code, player_name)
        
        if will_data:
            return jsonify({'will': will_data})
        else:
            return jsonify({'will': None})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/player/<player_name>/will', methods=['POST'])
def save_player_will_route(room_code, player_name):
    """Save player's last will"""
    try:
        data = request.get_json()
        will_content = data.get('will', '')
        
        success, message = game_engine.save_last_will(room_code, player_name, will_content)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/revealed-wills', methods=['GET'])
def get_revealed_wills_route(room_code):
    """Get all revealed wills"""
    try:
        wills = game_engine.get_revealed_wills(room_code)
        return jsonify({'revealed_wills': wills})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/death-note', methods=['POST'])
def save_death_note_route(room_code):
    """Save death note from killer to victim"""
    try:
        data = request.get_json()
        killer_name = data.get('killer_name')
        victim_name = data.get('victim_name')
        death_note = data.get('death_note', '')
        
        if not killer_name or not victim_name:
            return jsonify({'error': 'killer_name and victim_name required'}), 400
        
        success, message = game_engine.save_death_note(room_code, killer_name, victim_name, death_note)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/death-note-targets', methods=['GET'])
def get_death_note_targets_route(room_code):
    """Get available targets for death notes"""
    try:
        player_name = request.args.get('player_name')
        if not player_name:
            return jsonify({'error': 'player_name required'}), 400
        
        targets = game_engine.get_available_death_note_targets(room_code, player_name)
        return jsonify({'targets': targets})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gameplay_bp.route('/games/<room_code>/death-notes', methods=['GET'])
def get_death_notes_history_route(room_code):
    """Get revealed death notes history"""
    try:
        notes = game_engine.get_death_notes_history(room_code)
        return jsonify({'death_notes': notes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

