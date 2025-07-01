#!/usr/bin/env python3
"""
Serveur de test simple pour valider les corrections de synchronisation
"""

import json
import uuid
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
from enum import Enum

class Phase(Enum):
    WAITING = "waiting"
    LOBBY = "lobby"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    TRANSITION = "events"
    ENDED = "ended"

class TestGameEngine:
    def __init__(self):
        self.games = {}
    
    def create_game(self, name, max_players=8):
        game_id = str(uuid.uuid4())[:8]
        self.games[game_id] = {
            'id': game_id,
            'name': name,
            'max_players': max_players,
            'players': [],
            'status': 'waiting',
            'phase': Phase.WAITING,
            'host': None,
            'created_at': datetime.now(),
            'phase_start_time': None,
            'phase_duration': 0,
            'day_count': 0,
            'winner': None,
            'roles': {}
        }
        return game_id
    
    def join_game(self, game_id, player_name):
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if len(game['players']) >= game['max_players']:
            return False, "Game is full"
        
        if player_name in game['players']:
            return False, "Player already in game"
        
        game['players'].append(player_name)
        
        # Premier joueur devient l'hôte
        if len(game['players']) == 1:
            game['host'] = player_name
        
        return True, "Joined successfully"
    
    def start_game(self, game_id):
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if len(game['players']) < 4:
            return False, "Need at least 4 players"
        
        # 🔧 CORRECTION : Commencer par la phase LOBBY
        game['status'] = 'active'
        game['phase'] = Phase.LOBBY
        game['phase_start_time'] = datetime.now()
        game['phase_duration'] = 10  # 10 secondes pour la phase lobby
        game['day_count'] = 1
        
        # Attribution des rôles
        self._assign_roles(game)
        
        # Programmer la transition vers NIGHT
        timer = threading.Timer(10.0, self._advance_to_night, [game_id])
        timer.daemon = True
        timer.start()
        
        print(f"DEBUG: Game {game_id} started in LOBBY phase")
        return True, "Game started"
    
    def _assign_roles(self, game):
        """Attribuer les rôles aux joueurs"""
        players = game['players'].copy()
        num_players = len(players)
        
        # Configuration des rôles simple
        num_werewolves = max(1, num_players // 4)
        roles = ['werewolf'] * num_werewolves + ['villager'] * (num_players - num_werewolves)
        
        # Attribution aléatoire (simple)
        import random
        random.shuffle(roles)
        
        for i, player in enumerate(players):
            game['roles'][player] = {
                'role': roles[i],
                'alive': True
            }
        
        print(f"DEBUG: Roles assigned for game {game['id']}: {game['roles']}")
    
    def _advance_to_night(self, game_id):
        """Faire passer le jeu de LOBBY à NIGHT"""
        if game_id in self.games:
            game = self.games[game_id]
            if game['phase'] == Phase.LOBBY:
                game['phase'] = Phase.NIGHT
                game['phase_start_time'] = datetime.now()
                game['phase_duration'] = 60
                print(f"DEBUG: Game {game_id} advanced to NIGHT phase")
    
    def get_game_state(self, game_id):
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        # 🔧 CORRECTION : Ne pas vérifier la fin de jeu pendant LOBBY
        if (game['status'] == 'active' and 
            game['phase'] not in [Phase.ENDED, Phase.LOBBY] and
            game['day_count'] >= 1):
            winner = self._check_game_end(game)
            if winner:
                game['status'] = 'ended'
                game['winner'] = winner
                game['phase'] = Phase.ENDED
        
        # Calculer le temps restant
        time_remaining = 0
        if game['phase_start_time'] and game['phase_duration'] > 0:
            elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
            time_remaining = max(0, game['phase_duration'] - elapsed)
        
        return {
            'id': game['id'],
            'name': game['name'],
            'status': game['status'],
            'phase': game['phase'].value,
            'players': game['players'],
            'max_players': game['max_players'],
            'host': game['host'],
            'day_count': game['day_count'],
            'time_remaining': int(time_remaining),
            'winner': game['winner']
        }
    
    def _check_game_end(self, game):
        """Vérifier si le jeu doit se terminer"""
        alive_players = [p for p, data in game['roles'].items() if data['alive']]
        werewolves = [p for p, data in game['roles'].items() if data['role'] == 'werewolf' and data['alive']]
        villagers = [p for p, data in game['roles'].items() if data['role'] == 'villager' and data['alive']]
        
        if len(werewolves) == 0:
            return "villagers"
        elif len(werewolves) >= len(villagers):
            return "werewolves"
        
        return None
    
    def get_player_role(self, game_id, player_name):
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        if player_name in game['roles']:
            return game['roles'][player_name]
        
        return None

# Instance globale du moteur de jeu
game_engine = TestGameEngine()

class TestServerHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Routes GET
        if path == '/api/games':
            # Lister toutes les parties
            games = []
            for game_id, game_data in game_engine.games.items():
                state = game_engine.get_game_state(game_id)
                if state:
                    games.append(state)
            
            response = {'games': games}
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith('/api/games/') and path.endswith('/state'):
            # État d'une partie spécifique
            game_id = path.split('/')[3]
            state = game_engine.get_game_state(game_id)
            
            if state:
                self.wfile.write(json.dumps(state).encode())
            else:
                self.send_error(404, "Game not found")
                
        elif '/player/' in path and path.endswith('/role'):
            # Rôle d'un joueur
            parts = path.split('/')
            game_id = parts[3]
            player_name = parts[5]
            
            role_data = game_engine.get_player_role(game_id, player_name)
            
            if role_data:
                self.wfile.write(json.dumps(role_data).encode())
            else:
                self.send_error(404, "Player role not found")
        
        else:
            self.send_error(404, "Route not found")
    
    def do_POST(self):
        """Gérer les requêtes POST"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Lire le contenu de la requête
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode()) if post_data else {}
        except:
            data = {}
        
        # Headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        
        # Routes POST
        if path == '/api/games':
            # Créer une nouvelle partie
            name = data.get('name', 'Test Game')
            max_players = data.get('max_players', 8)
            
            game_id = game_engine.create_game(name, max_players)
            
            self.send_response(201)
            self.end_headers()
            
            response = {'game_id': game_id, 'message': 'Game created successfully'}
            self.wfile.write(json.dumps(response).encode())
            
        elif path.endswith('/join'):
            # Rejoindre une partie
            game_id = path.split('/')[3]
            player_name = data.get('player_name')
            
            if not player_name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Player name required'}).encode())
                return
            
            success, message = game_engine.join_game(game_id, player_name)
            
            if success:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'message': message}).encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'error': message}).encode())
                
        elif path.endswith('/start'):
            # Démarrer une partie
            game_id = path.split('/')[3]
            
            success, message = game_engine.start_game(game_id)
            
            if success:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'message': message}).encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'error': message}).encode())
        
        else:
            self.send_error(404, "Route not found")
    
    def log_message(self, format, *args):
        """Supprimer les logs par défaut pour plus de clarté"""
        pass

def run_test_server():
    """Lancer le serveur de test"""
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, TestServerHandler)
    
    print("🚀 Serveur de test démarré sur http://localhost:5000")
    print("✅ Routes disponibles:")
    print("   GET  /api/games - Lister les parties")
    print("   POST /api/games - Créer une partie")
    print("   POST /api/games/{id}/join - Rejoindre une partie")
    print("   POST /api/games/{id}/start - Démarrer une partie")
    print("   GET  /api/games/{id}/state - État d'une partie")
    print("   GET  /api/games/{id}/player/{name}/role - Rôle d'un joueur")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Serveur arrêté")
        httpd.shutdown()

if __name__ == '__main__':
    run_test_server()