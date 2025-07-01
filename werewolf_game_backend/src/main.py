import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from src.models.game import db, Game, Player
from src.routes.user import user_bp
from src.routes.game import game_bp
from src.routes.gameplay import gameplay_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(game_bp, url_prefix='/api')
app.register_blueprint(gameplay_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# SocketIO events for real-time communication
@socketio.on('join_room')
def on_join_room(data):
    from flask_socketio import join_room, emit
    room_code = data.get('room_code')
    player_name = data.get('player_name')
    
    if room_code and player_name:
        join_room(room_code)
        emit('player_joined', {
            'player_name': player_name,
            'message': f'{player_name} joined the room'
        }, room=room_code)

@socketio.on('leave_room')
def on_leave_room(data):
    from flask_socketio import leave_room, emit
    room_code = data.get('room_code')
    player_name = data.get('player_name')
    
    if room_code and player_name:
        leave_room(room_code)
        emit('player_left', {
            'player_name': player_name,
            'message': f'{player_name} left the room'
        }, room=room_code)

@socketio.on('player_ready')
def on_player_ready(data):
    from flask_socketio import emit
    room_code = data.get('room_code')
    player_name = data.get('player_name')
    is_ready = data.get('is_ready')
    
    if room_code and player_name:
        emit('player_ready_update', {
            'player_name': player_name,
            'is_ready': is_ready
        }, room=room_code)

@socketio.on('game_action')
def on_game_action(data):
    from flask_socketio import emit
    room_code = data.get('room_code')
    action_type = data.get('action_type')
    player_name = data.get('player_name')
    
    if room_code and action_type:
        emit('game_update', {
            'action_type': action_type,
            'player_name': player_name,
            'data': data
        }, room=room_code)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
