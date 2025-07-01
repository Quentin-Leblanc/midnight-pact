from enum import Enum
import random
from datetime import datetime, timedelta

class Role(Enum):
    VILLAGER = "villager"
    WEREWOLF = "werewolf"
    SEER = "seer"
    WITCH = "witch"
    GUARD = "guard"
    HUNTER = "hunter"

class Phase(Enum):
    WAITING = "waiting"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"

class GameEngine:
    def __init__(self):
        self.games = {}
    
    def create_game(self, game_id, name, max_players):
        """Create a new game instance"""
        self.games[game_id] = {
            'id': game_id,
            'name': name,
            'max_players': max_players,
            'players': {},
            'status': 'waiting',
            'phase': Phase.WAITING,
            'phase_start_time': None,
            'phase_duration': 0,  # in seconds
            'day_count': 0,
            'night_actions': {},
            'votes': {},
            'eliminated_players': [],
            'winner': None,
            'chat_messages': [],
            'last_elimination': None,
            'phase_history': [],
            'game_history': []  # Historique détaillé des événements
        }
        return self.games[game_id]
    
    def add_player(self, game_id, player_name):
        """Add a player to the game"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if game['status'] != 'waiting':
            return False, "Game already started"
        
        if len(game['players']) >= game['max_players']:
            return False, "Game is full"
        
        if player_name in game['players']:
            return False, "Player name already taken"
        
        game['players'][player_name] = {
            'name': player_name,
            'role': None,
            'alive': True,
            'protected': False,
            'has_voted': False,
            'vote_target': None,
            'night_action_used': False,
            'witch_heal_used': False,
            'witch_poison_used': False,
            'last_will': ''
        }
        
        return True, "Player added successfully"
    
    def start_game(self, game_id):
        """Start the game and assign roles"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if len(game['players']) < 4:
            return False, "Need at least 4 players to start"
        
        # Assign roles
        self._assign_roles(game)
        
        # Start first night
        game['status'] = 'in_progress'
        game['phase'] = Phase.NIGHT
        game['day_count'] = 1
        game['phase_start_time'] = datetime.now()
        game['phase_duration'] = 60  # 60 seconds for night phase
        
        game['phase_history'].append({
            'phase': Phase.NIGHT.value,
            'day': game['day_count'],
            'start_time': game['phase_start_time'].isoformat(),
            'duration': game['phase_duration']
        })
        
        return True, "Game started successfully"
    
    def _assign_roles(self, game):
        """Assign roles to players based on game size"""
        player_count = len(game['players'])
        player_names = list(game['players'].keys())
        random.shuffle(player_names)
        
        # Role distribution based on player count
        if player_count <= 6:
            werewolves = 1
            special_roles = 2  # seer + witch
        elif player_count <= 10:
            werewolves = 2
            special_roles = 3  # seer + witch + guard
        else:
            werewolves = 3
            special_roles = 4  # seer + witch + guard + hunter
        
        roles_to_assign = []
        
        # Add werewolves
        for _ in range(werewolves):
            roles_to_assign.append(Role.WEREWOLF)
        
        # Add special roles
        roles_to_assign.append(Role.SEER)
        roles_to_assign.append(Role.WITCH)
        
        if special_roles >= 3:
            roles_to_assign.append(Role.GUARD)
        if special_roles >= 4:
            roles_to_assign.append(Role.HUNTER)
        
        # Fill remaining with villagers
        while len(roles_to_assign) < player_count:
            roles_to_assign.append(Role.VILLAGER)
        
        # Assign roles to players
        for i, player_name in enumerate(player_names):
            game['players'][player_name]['role'] = roles_to_assign[i]
            print(f"DEBUG: Assigned {roles_to_assign[i].value} to {player_name}")
    
    def get_game_state(self, game_id):
        """Get current game state"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        # Calculate remaining time for current phase
        remaining_time = 0
        if game['phase_start_time'] and game['phase_duration']:
            elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
            remaining_time = max(0, game['phase_duration'] - elapsed)
            
            # Auto-advance phase if time is up OR if all players have voted during day phase
            should_advance = False
            if remaining_time == 0 and game['phase'] != Phase.ENDED and game['status'] == 'in_progress':
                should_advance = True
            elif game['phase'] == Phase.DAY and game['status'] == 'in_progress':
                # Check if all alive players have voted (and we're in voting period)
                alive_players = [p for p in game['players'].values() if p['alive']]
                voted_players = [p for p in alive_players if p.get('has_voted', False)]
                if len(voted_players) == len(alive_players) and len(alive_players) > 0 and remaining_time <= 30:
                    should_advance = True
            
            if should_advance:
                self.advance_phase(game_id)
                # Recalculate remaining time after phase advance
                if game['phase_start_time'] and game['phase_duration']:
                    elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
                    remaining_time = max(0, game['phase_duration'] - elapsed)
        
        # Calculate vote counts for each player
        vote_counts = {}
        if game['phase'] == Phase.DAY:
            for player_name, player in game['players'].items():
                if player['alive'] and player.get('vote_target'):
                    target = player['vote_target']
                    vote_counts[target] = vote_counts.get(target, 0) + 1

        return {
            'id': game['id'],
            'name': game['name'],
            'status': game['status'],
            'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
            'day_count': game['day_count'],
            'day_number': game['day_count'],  # Alias pour la compatibilité frontend
            'remaining_time': int(remaining_time),
            'phase_duration': game['phase_duration'],
            'game_history': game.get('game_history', []),
            'players': [
                {
                    'name': name,
                    'alive': player['alive'],
                    'has_voted': player.get('has_voted', False),
                    'role': player['role'].value if isinstance(player['role'], Role) and not player['alive'] else None,
                    'vote_count': vote_counts.get(name, 0),
                    'last_will': player.get('last_will', '') if not player['alive'] else None
                }
                for name, player in game['players'].items()
            ],
            'alive_players': len([p for p in game['players'].values() if p['alive']]),
            'total_players': len(game['players']),
            'last_elimination': game.get('last_elimination'),
            'winner': game.get('winner'),
            'chat_messages': game.get('chat_messages', []),
            'vote_counts': vote_counts
        }
    
    def get_player_role(self, game_id, player_name):
        """Get player's role and specific information"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return None
        
        player = game['players'][player_name]
        role_info = {
            'role': player['role'].value if isinstance(player['role'], Role) else player['role'],
            'alive': player['alive'],
            'protected': player.get('protected', False),
            'night_action_used': player.get('night_action_used', False)
        }
        
        # Add role-specific information
        if player['role'] == Role.WEREWOLF:
            # Werewolves can see other werewolves
            role_info['werewolf_team'] = [
                name for name, p in game['players'].items() 
                if p['role'] == Role.WEREWOLF and p['alive']
            ]
        elif player['role'] == Role.WITCH:
            role_info['heal_used'] = player.get('witch_heal_used', False)
            role_info['poison_used'] = player.get('witch_poison_used', False)
        
        return role_info
    
    def perform_night_action(self, game_id, player_name, action, target=None):
        """Perform a night action"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if game['phase'] != Phase.NIGHT:
            return False, "Not night phase"
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        player = game['players'][player_name]
        
        if not player['alive']:
            return False, "Dead players cannot perform actions"
        
        # Store the action
        if player_name not in game['night_actions']:
            game['night_actions'][player_name] = {}
        
        game['night_actions'][player_name][action] = target
        player['night_action_used'] = True
        
        # Return more specific messages based on action type
        if action == 'kill':
            return True, f"Vous avez choisi d'éliminer {target}"
        elif action == 'investigate':
            # For seer, we can give the result immediately
            if target in game['players']:
                target_role = game['players'][target]['role']
                if target_role == Role.WEREWOLF:
                    return True, f"Vous découvrez que {target} est un Loup-Garou !"
                else:
                    return True, f"Vous découvrez que {target} est un Villageois"
            return True, "Investigation effectuée"
        elif action == 'protect':
            return True, f"Vous protégez {target} cette nuit"
        elif action == 'heal':
            return True, "Vous utilisez votre potion de guérison"
        elif action == 'poison':
            return True, f"Vous empoisonnez {target}"
        
        return True, "Action enregistrée"
    
    def advance_phase(self, game_id):
        """Advance to the next phase"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if game['phase'] == Phase.NIGHT:
            # Process night actions
            self._process_night_actions(game)
            
            # Check for game end
            if self._check_game_end(game):
                return True, f"Game ended. Winner: {game['winner']}"
            
            # Move to day phase
            game['phase'] = Phase.DAY
            game['phase_start_time'] = datetime.now()
            game['phase_duration'] = 60  # 1 minute for day discussion + voting
            
        elif game['phase'] == Phase.DAY:
            # Process votes and eliminate player (voting happens during day phase)
            eliminated = self._process_votes(game)
            
            # Check for game end
            if self._check_game_end(game):
                return True, f"Game ended. Winner: {game['winner']}"
            
            # Move to next night
            game['day_count'] += 1
            game['phase'] = Phase.NIGHT
            game['phase_start_time'] = datetime.now()
            game['phase_duration'] = 60  # 60 seconds for night phase
            
            # Reset night actions and votes
            game['night_actions'] = {}
            game['votes'] = {}
            for player in game['players'].values():
                player['has_voted'] = False
                player['vote_target'] = None
                player['night_action_used'] = False
                player['protected'] = False
        
        # Add to phase history
        game['phase_history'].append({
            'phase': game['phase'].value,
            'day': game['day_count'],
            'start_time': game['phase_start_time'].isoformat(),
            'duration': game['phase_duration']
        })
        
        # Ajouter l'événement de changement de phase à l'historique
        game['game_history'].append({
            'type': 'phase_change',
            'phase': game['phase'].value,
            'day': game['day_count'],
            'description': f"Début de la phase {game['phase'].value} du tour {game['day_count']}"
        })
        
        return True, f"Advanced to {game['phase'].value}"
    
    def _process_night_actions(self, game):
        """Process all night actions"""
        # First, apply protection
        for player_name, actions in game['night_actions'].items():
            if 'protect' in actions:
                target = actions['protect']
                if target in game['players']:
                    game['players'][target]['protected'] = True
        
        # Then, apply attacks (werewolf kills)
        werewolf_target = None
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            if player['role'] == Role.WEREWOLF and 'kill' in actions:
                werewolf_target = actions['kill']
                break
        
        # Apply witch heal/poison
        witch_heal_target = None
        witch_poison_target = None
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            if player['role'] == Role.WITCH:
                if 'heal' in actions:
                    witch_heal_target = actions['heal']
                    player['witch_heal_used'] = True
                if 'poison' in actions:
                    witch_poison_target = actions['poison']
                    player['witch_poison_used'] = True
        
        # Resolve deaths
        if werewolf_target and werewolf_target in game['players']:
            target_player = game['players'][werewolf_target]
            # Check if protected or healed
            if not target_player['protected'] and werewolf_target != witch_heal_target:
                target_player['alive'] = False
                eliminated_info = {
                    'name': werewolf_target,
                    'cause': 'werewolf_kill',
                    'day': game['day_count'],
                    'role': target_player['role'].value if isinstance(target_player['role'], Role) else target_player['role']
                }
                game['eliminated_players'].append(eliminated_info)
                game['last_elimination'] = f"{werewolf_target} was killed by werewolves"
                
                # Ajouter à l'historique
                game['game_history'].append({
                    'type': 'elimination',
                    'phase': 'night',
                    'day': game['day_count'],
                    'player': werewolf_target,
                    'cause': 'werewolf_kill',
                    'role': eliminated_info['role'],
                    'description': f"{werewolf_target} ({eliminated_info['role']}) a été tué par les loups-garous"
                })
        
        # Apply witch poison
        if witch_poison_target and witch_poison_target in game['players']:
            game['players'][witch_poison_target]['alive'] = False
            eliminated_info = {
                'name': witch_poison_target,
                'cause': 'witch_poison',
                'day': game['day_count'],
                'role': game['players'][witch_poison_target]['role'].value if isinstance(game['players'][witch_poison_target]['role'], Role) else game['players'][witch_poison_target]['role']
            }
            game['eliminated_players'].append(eliminated_info)
            
            # Ajouter à l'historique
            game['game_history'].append({
                'type': 'elimination',
                'phase': 'night',
                'day': game['day_count'],
                'player': witch_poison_target,
                'cause': 'witch_poison',
                'role': eliminated_info['role'],
                'description': f"{witch_poison_target} ({eliminated_info['role']}) a été empoisonné par la sorcière"
            })
    
    def _process_votes(self, game):
        """Process voting and eliminate the player with most votes"""
        vote_counts = {}
        
        for player_name, player in game['players'].items():
            if player['alive'] and player.get('vote_target'):
                target = player['vote_target']
                vote_counts[target] = vote_counts.get(target, 0) + 1
        
        if vote_counts:
            # Find player with most votes
            max_votes = max(vote_counts.values())
            candidates = [name for name, votes in vote_counts.items() if votes == max_votes]
            
            if len(candidates) == 1:
                eliminated = candidates[0]
                eliminated_player = game['players'][eliminated]
                eliminated_player['alive'] = False
                
                eliminated_info = {
                    'name': eliminated,
                    'cause': 'voted_out',
                    'day': game['day_count'],
                    'votes': max_votes,
                    'role': eliminated_player['role'].value if isinstance(eliminated_player['role'], Role) else eliminated_player['role']
                }
                game['eliminated_players'].append(eliminated_info)
                game['last_elimination'] = f"{eliminated} was voted out ({max_votes} votes)"
                
                # Ajouter à l'historique
                game['game_history'].append({
                    'type': 'elimination',
                    'phase': 'day',
                    'day': game['day_count'],
                    'player': eliminated,
                    'cause': 'voted_out',
                    'role': eliminated_info['role'],
                    'votes': max_votes,
                    'description': f"{eliminated} ({eliminated_info['role']}) a été éliminé par vote ({max_votes} votes)"
                })
                
                # Hunter revenge
                if game['players'][eliminated]['role'] == Role.HUNTER:
                    # Hunter can kill someone when eliminated
                    # This would need additional UI handling
                    pass
                
                return eliminated
        
        return None
    
    def cast_vote(self, game_id, player_name, target):
        """Cast a vote during day phase (last 30 seconds)"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if game['phase'] != Phase.DAY:
            return False, "Not day phase"
        
        # Check if we're in the voting period (last 30 seconds)
        if game['phase_start_time'] and game['phase_duration']:
            elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
            remaining_time = max(0, game['phase_duration'] - elapsed)
            if remaining_time > 30:
                return False, "Vote not available yet (wait for last 30 seconds)"
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        player = game['players'][player_name]
        
        if not player['alive']:
            return False, "Dead players cannot vote"
        
        if target not in game['players'] or not game['players'][target]['alive']:
            return False, "Invalid vote target"
        
        player['vote_target'] = target
        player['has_voted'] = True
        
        return True, "Vote cast successfully"
    
    def _check_game_end(self, game):
        """Check if the game has ended"""
        alive_players = [p for p in game['players'].values() if p['alive']]
        alive_werewolves = [p for p in alive_players if p['role'] == Role.WEREWOLF]
        alive_villagers = [p for p in alive_players if p['role'] != Role.WEREWOLF]
        
        if len(alive_werewolves) == 0:
            game['winner'] = 'villagers'
            game['phase'] = Phase.ENDED
            return True
        elif len(alive_werewolves) >= len(alive_villagers):
            game['winner'] = 'werewolves'
            game['phase'] = Phase.ENDED
            return True
        
        return False
    
    def add_chat_message(self, game_id, player_name, message):
        """Add a chat message (only during day phase)"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if game['phase'] != Phase.DAY:
            return False, "Chat only available during day phase"
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        if not game['players'][player_name]['alive']:
            return False, "Dead players cannot chat"
        
        chat_message = {
            'player': player_name,
            'player_name': player_name,  # Ajout pour la compatibilité frontend
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'day': game['day_count']
        }
        
        game['chat_messages'].append(chat_message)
        
        return True, "Message added"
    
    def get_available_actions(self, game_id, player_name):
        """Get available actions for a player based on their role and game phase"""
        if game_id not in self.games:
            return []
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return []
        
        player = game['players'][player_name]
        
        if not player['alive']:
            return []
        
        actions = []
        
        if game['phase'] == Phase.NIGHT and not player.get('night_action_used', False):
            alive_players = [name for name, p in game['players'].items() if p['alive'] and name != player_name]
            
            if player['role'] == Role.WEREWOLF:
                actions.append({
                    'type': 'kill',
                    'description': 'Choose a player to eliminate',
                    'targets': alive_players
                })
            elif player['role'] == Role.SEER:
                actions.append({
                    'type': 'investigate',
                    'description': 'Investigate a player\'s role',
                    'targets': alive_players
                })
            elif player['role'] == Role.GUARD:
                actions.append({
                    'type': 'protect',
                    'description': 'Protect a player from werewolf attack',
                    'targets': alive_players
                })
            elif player['role'] == Role.WITCH:
                if not player.get('witch_heal_used', False):
                    actions.append({
                        'type': 'heal',
                        'description': 'Use healing potion',
                        'targets': []
                    })
                if not player.get('witch_poison_used', False):
                    actions.append({
                        'type': 'poison',
                        'description': 'Use poison on a player',
                        'targets': alive_players
                    })
        
        elif game['phase'] == Phase.DAY:
            # Check if we're in the voting period (last 30 seconds)
            can_vote = False
            if game['phase_start_time'] and game['phase_duration']:
                elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
                remaining_time = max(0, game['phase_duration'] - elapsed)
                can_vote = remaining_time <= 30
            
            if can_vote:
                alive_players = [name for name, p in game['players'].items() if p['alive'] and name != player_name]
                vote_description = 'Change your vote' if player.get('has_voted', False) else 'Vote to eliminate a player'
                actions.append({
                    'type': 'vote',
                    'description': vote_description,
                    'targets': alive_players,
                    'current_vote': player.get('vote_target', None)
                })
        
        return actions

    def save_last_will(self, game_id, player_name, last_will):
        """Save a player's last will"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        game['players'][player_name]['last_will'] = last_will
        return True, "Last will saved"

# Global game engine instance
game_engine = GameEngine()

