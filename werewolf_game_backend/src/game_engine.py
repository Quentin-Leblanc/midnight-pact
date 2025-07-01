from enum import Enum
import random
from datetime import datetime, timedelta

class Role(Enum):
    VILLAGER = "villager"
    WEREWOLF = "werewolf"
    SEER = "seer"
    WITCH = "witch"
    GUARD = "bodyguard"
    HUNTER = "hunter"
    # 🆕 CHAPITRE 2 - RÔLES INVESTIGATIFS
    SHERIFF = "sheriff"           # Détecte "Suspect" vs "Not Suspicious"  
    INVESTIGATOR = "investigator" # Donne indices sur type de rôle

class Phase(Enum):
    WAITING = "waiting"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    TRIAL = "trial"          # 🆕 Phase de procès
    LYNCHING = "lynching"    # 🆕 Phase d'exécution
    TRANSITION = "events"
    ENDED = "ended"

class VoteType(Enum):
    MAJORITY = "majority"                    # 51% pour lynch direct
    MAJORITY_TRIAL = "majority_trial"        # 51% pour procès
    BALLOT = "ballot"                        # Vote secret, plus de votes = lynch
    BALLOT_TRIAL = "ballot_trial"            # Vote secret puis procès

class TrialVerdict(Enum):
    INNOCENT = "innocent"
    GUILTY = "guilty"

class ChatChannel(Enum):
    PUBLIC = "public"           # Chat visible par tous
    MAFIA = "mafia"            # Chat privé des mafia
    TRIAD = "triad"            # Chat privé des triad  
    DEAD = "dead"              # Chat des morts
    PRIVATE = "private"        # Messages privés

# 🆕 CHAPITRE 2 - ENUMS INVESTIGATION
class SheriffResult(Enum):
    SUSPICIOUS = "suspicious"       # Cible suspecte (mafia/evil)
    NOT_SUSPICIOUS = "not_suspicious"  # Cible non suspecte (town/neutral)

class InvestigationGroup(Enum):
    # Groupes d'investigation selon SC2 Mafia
    PROTECTORS = "protectors"       # Bodyguard, Lookout, Spy
    INVESTIGATORS = "investigators"  # Sheriff, Investigator, Detective  
    KILLERS = "killers"            # Vigilante, Veteran, Werewolf
    SUPPORT = "support"            # Citizen, Mayor, Mason
    WITCHES = "witches"            # Witch, Witch Doctor
    NEUTRALS = "neutrals"          # Survivor, Amnesiac, etc.

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
            'trial_votes': {},               # 🆕 Votes innocent/coupable
            'eliminated_players': [],
            'winner': None,
            'chat_messages': [],
            'mafia_chat': [],               # 🆕 Chat nocturne mafia
            'triad_chat': [],               # 🆕 Chat nocturne triad
            'dead_chat': [],                # 🆕 Chat des morts
            'private_messages': [],         # 🆕 Messages privés
            'night_chat_enabled': True,     # 🆕 Chat nocturne activé
            'last_elimination': None,
            'last_wills': {},               # 🆕 Testaments des joueurs
            'death_notes': {},              # 🆕 Notes de mort des tueurs
            'revealed_wills': [],           # 🆕 Testaments révélés publiquement
            'investigation_results': {},    # 🆕 Résultats d'investigation par joueur
            'investigation_history': [],   # 🆕 Historique des investigations
            'phase_history': [],
            'game_history': [],
            
            # 🆕 Système de procès
            'vote_type': VoteType.MAJORITY_TRIAL,  # Type de vote par défaut
            'accused_player': None,               # Joueur en procès
            'trial_defense_time': 30,             # Temps de défense en secondes
            'trial_voting_time': 30,              # Temps de vote innocent/coupable
            'trial_pauses_day': True,             # Le procès pause le timer jour
            'anonymous_ballot': False,            # Vote secret ou public
            'lynch_threshold': 0.51,              # Seuil pour lynch (51%)
            
            # 🆕 Historique des procès
            'trial_history': [],
            'day_voting_enabled': True,           # Vote activé pendant la journée
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
        
        # Clear chat messages from waiting phase
        game['chat_messages'] = []
        
        # Start first night
        game['status'] = 'active'
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
        """Assign roles to players based on game size - 🆕 CHAPITRE 2 avec Sheriff & Investigator"""
        player_count = len(game['players'])
        player_names = list(game['players'].keys())
        random.shuffle(player_names)
        
        # 🆕 Distribution des rôles élargie pour Chapitre 2
        if player_count <= 6:
            werewolves = 1
            special_roles = 3  # seer + witch + sheriff OU investigator
        elif player_count <= 10:
            werewolves = 2
            special_roles = 4  # seer + witch + guard + sheriff OU investigator
        else:
            werewolves = 3
            special_roles = 6  # seer + witch + guard + hunter + sheriff + investigator
        
        roles_to_assign = []
        
        # Add werewolves
        for _ in range(werewolves):
            roles_to_assign.append(Role.WEREWOLF)
        
        # Add core special roles (toujours présents)
        roles_to_assign.append(Role.SEER)
        roles_to_assign.append(Role.WITCH)
        
        # 🆕 Ajouter rôles investigatifs selon taille
        if special_roles >= 3:
            # Choisir aléatoirement Sheriff OU Investigator pour petites parties
            investigation_role = random.choice([Role.SHERIFF, Role.INVESTIGATOR])
            roles_to_assign.append(investigation_role)
            
        if special_roles >= 4:
            roles_to_assign.append(Role.GUARD)
            
        if special_roles >= 5:
            roles_to_assign.append(Role.HUNTER)
            
        if special_roles >= 6:
            # Pour grandes parties, ajouter l'autre rôle investigatif
            if Role.SHERIFF not in roles_to_assign:
                roles_to_assign.append(Role.SHERIFF)
            elif Role.INVESTIGATOR not in roles_to_assign:
                roles_to_assign.append(Role.INVESTIGATOR)
        
        # Fill remaining with villagers
        while len(roles_to_assign) < player_count:
            roles_to_assign.append(Role.VILLAGER)
        
        # Assign roles to players
        for i, player_name in enumerate(player_names):
            game['players'][player_name]['role'] = roles_to_assign[i]
            print(f"DEBUG: Assigned {roles_to_assign[i].value} to {player_name}")
            
        print(f"🆕 CHAPITRE 2: Distribution finale - {[r.value for r in roles_to_assign]}")
    
    def get_game_state(self, game_id):
        """Get current game state"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        # Vérifier d'abord si le jeu doit se terminer
        if game['status'] == 'active' and game['phase'] != Phase.ENDED:
            if self._check_game_end(game):
                # Le jeu vient de se terminer
                game['status'] = 'ended'
        
        # Calculate remaining time for current phase
        remaining_time = 0
        if game['phase_start_time'] and game['phase_duration']:
            elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
            remaining_time = max(0, game['phase_duration'] - elapsed)
            
            # Auto-advance phase if time is up OR if all players have voted during day phase
            should_advance = False
            if remaining_time == 0 and game['phase'] != Phase.ENDED and game['status'] == 'active':
                should_advance = True
            elif game['phase'] == Phase.DAY and game['status'] == 'active':
                # Check if all alive players have voted (and we're in voting period)
                alive_players = [p for p in game['players'].values() if p['alive']]
                voted_players = [p for p in alive_players if p.get('has_voted', False)]
                if len(voted_players) == len(alive_players) and len(alive_players) > 0 and remaining_time <= 30:
                    should_advance = True
            
            if should_advance:
                print(f"DEBUG: Auto-advancing phase for game {game_id}, current phase: {game['phase']}, remaining_time: {remaining_time}")
                success, message = self.advance_phase(game_id)
                print(f"DEBUG: Advance result: {success}, {message}")
                # Recalculate remaining time after phase advance
                if game['phase_start_time'] and game['phase_duration']:
                    elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
                    remaining_time = max(0, game['phase_duration'] - elapsed)
        
        # Calculate vote counts for each player (pendant DAY et VOTING phases)
        vote_counts = {}
        if game['phase'] in [Phase.DAY, Phase.VOTING]:
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
                    'vote_target': player.get('vote_target') if player['alive'] else None,  # Cible de vote actuelle
                    'role': player['role'].value if isinstance(player['role'], Role) and not player['alive'] else None,
                    'vote_count': vote_counts.get(name, 0),
                    'last_will': player.get('last_will', '') if not player['alive'] else None
                }
                for name, player in game['players'].items()
            ],
            'vote_counts': vote_counts,  # Ajout des totaux de votes
            'chat_messages': game['chat_messages'],
            'winner': game.get('winner'),
            'last_elimination': game.get('last_elimination'),
            'transition_type': game.get('transition_type'),
            'alive_players': len([p for p in game['players'].values() if p['alive']]),
            'total_players': len(game['players'])
        }
    
    def get_player_role(self, game_id, player_name):
        """Get player's role information"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return None
        
        player = game['players'][player_name]
        
        role_info = {
            'role': player['role'].value if isinstance(player['role'], Role) else player['role'],
            'alive': player['alive'],
            'heal_used': player.get('witch_heal_used', False),
            'poison_used': player.get('witch_poison_used', False)
        }
        
        # Add werewolf team info
        if player['role'] == Role.WEREWOLF:
            werewolf_team = [name for name, p in game['players'].items() 
                           if p['role'] == Role.WEREWOLF and p['alive']]
            role_info['werewolf_team'] = werewolf_team
        
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
            return False, "Dead players cannot act"
        
        # Les sorcières ne peuvent pas changer d'avis sur leurs potions
        if player.get('night_action_used', False) and player['role'] == Role.WITCH:
            return False, "Already used night action"
        
        # Initialize night actions if not exists
        if player_name not in game['night_actions']:
            game['night_actions'][player_name] = {}
        
        # Validate action based on role
        if player['role'] == Role.WEREWOLF and action == 'kill':
            game['night_actions'][player_name]['kill'] = target
            return True, f"Vous avez choisi de tuer {target}. Vous pouvez changer votre choix avant la fin de la nuit."
        elif player['role'] == Role.SEER and action == 'investigate':
            # Vérifier si la voyante a déjà utilisé son action cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            game['night_actions'][player_name]['investigate'] = target
            player['night_action_used'] = True  # Marquer l'action comme utilisée
            
            # Révéler immédiatement le rôle de la cible à la voyante
            target_player = game['players'][target]
            target_role = target_player['role'].value if isinstance(target_player['role'], Role) else target_player['role']
            
            # Déterminer l'équipe
            if target_role == 'werewolf':
                role_info = f"{target} est un LOUP-GAROU ! 🐺"
            else:
                role_info = f"{target} est innocent (Rôle: {target_role}) ✅"
                
            return True, f"Vision révélée : {role_info}"
        elif player['role'] == Role.GUARD and action == 'protect':
            # Vérifier si le garde a déjà utilisé son action cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            game['night_actions'][player_name]['protect'] = target
            player['night_action_used'] = True  # Marquer l'action comme utilisée
            return True, f"Vous protégez {target} cette nuit."
        elif player['role'] == Role.WITCH and action in ['heal', 'poison']:
            if action == 'heal' and not player.get('witch_heal_used', False):
                game['night_actions'][player_name]['heal'] = target
                player['night_action_used'] = True  # Action définitive pour la sorcière
                return True, f"Vous avez utilisé votre potion de guérison sur {target}."
            elif action == 'poison' and not player.get('witch_poison_used', False):
                game['night_actions'][player_name]['poison'] = target
                player['night_action_used'] = True  # Action définitive pour la sorcière
                return True, f"Vous avez empoisonné {target}. Cette personne mourra à l'aube."
            else:
                return False, "Potion already used"
        
        # 🆕 CHAPITRE 2 - ACTIONS INVESTIGATIVES
        elif player['role'] == Role.SHERIFF and action == 'investigate':
            # Vérifier si le Sheriff a déjà utilisé son action cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
            
            if target and target in game['players'] and game['players'][target]['alive']:
                success, message = self.perform_sheriff_investigation(game_id, player_name, target)
                if success:
                    player['night_action_used'] = True
                return success, message
            else:
                return False, "Cible invalide pour l'investigation"
        
        elif player['role'] == Role.INVESTIGATOR and action == 'investigate':
            # Vérifier si l'Investigator a déjà utilisé son action cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
            
            if target and target in game['players'] and game['players'][target]['alive']:
                success, message = self.perform_investigator_investigation(game_id, player_name, target)
                if success:
                    player['night_action_used'] = True
                return success, message
            else:
                return False, "Cible invalide pour l'investigation"
        
        else:
            return False, "Invalid action for role"
    
    def advance_phase(self, game_id):
        """Advance to the next phase"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if game['phase'] == Phase.NIGHT:
            # Process night actions
            print(f"DEBUG: Processing night actions for game {game_id}")
            self._process_night_actions(game)
            
            # Check for game end
            if self._check_game_end(game):
                print(f"DEBUG: Game ended. Winner: {game['winner']}")
                return True, f"Game ended. Winner: {game['winner']}"
            
            # Move to transition phase (night results)
            print(f"DEBUG: Moving to transition phase (night results) for game {game_id}")
            game['phase'] = Phase.TRANSITION
            game['phase_start_time'] = datetime.now()
            game['phase_duration'] = 15  # 15 seconds to show night results
            game['transition_type'] = 'night_results'
            
        elif game['phase'] == Phase.TRANSITION:
            if game.get('transition_type') == 'night_results':
                # Transition from night results to day
                print(f"DEBUG: Moving from night results to day phase for game {game_id}")
                game['phase'] = Phase.DAY
                game['phase_start_time'] = datetime.now()
                game['phase_duration'] = 120  # 2 minutes for day discussion + voting
                game['transition_type'] = None
                game['day_voting_enabled'] = True  # 🆕 Réactiver les votes
                
            elif game.get('transition_type') == 'day_results':
                # Transition from day results to night
                print(f"DEBUG: Moving from day results to night phase for game {game_id}")
                game['day_count'] += 1
                game['phase'] = Phase.NIGHT
                game['phase_start_time'] = datetime.now()
                game['phase_duration'] = 60  # 60 seconds for night phase
                game['transition_type'] = None
                
                # Reset night actions and votes
                game['night_actions'] = {}
                game['votes'] = {}
                game['trial_votes'] = {}  # 🆕 Reset trial votes
                game['accused_player'] = None  # 🆕 Reset accused
                for player in game['players'].values():
                    player['has_voted'] = False
                    player['vote_target'] = None
                    player['night_action_used'] = False
                    player['protected'] = False
                    player['trial_vote'] = None  # 🆕 Reset trial vote
            
        elif game['phase'] == Phase.DAY:
            # 🆕 Vérifier si quelqu'un doit être mis en procès
            accused = self._check_for_trial(game)
            if accused:
                return self._start_trial(game, accused)
            else:
                # Pas de procès, passage direct à la nuit
                self._process_day_end(game)
            
        elif game['phase'] == Phase.TRIAL:
            # 🆕 Traiter les votes du procès
            return self._process_trial_votes(game)
            
        elif game['phase'] == Phase.LYNCHING:
            # 🆕 Exécuter et passer à la transition
            self._execute_accused(game)
            
            # Check for game end
            if self._check_game_end(game):
                return True, f"Game ended. Winner: {game['winner']}"
            
            # Move to transition phase (day results)
            print(f"DEBUG: Moving to transition phase (day results) for game {game_id}")
            game['phase'] = Phase.TRANSITION
            game['phase_start_time'] = datetime.now()
            game['phase_duration'] = 15  # 15 seconds to show day results
            game['transition_type'] = 'day_results'
        
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
        
        # Collect elimination stories for combined message
        elimination_stories = []
        
        # Resolve werewolf deaths
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
                elimination_stories.append(self._generate_death_story(werewolf_target, 'werewolf_kill', target_player['role']))
                
                # 🆕 Révéler testament et note de mort
                self.reveal_will_on_death(game, werewolf_target)
                
                # Trouver le tueur werewolf pour la note de mort
                werewolf_killer = None
                for player_name, actions in game['night_actions'].items():
                    player = game['players'][player_name]
                    if player['role'] == Role.WEREWOLF and 'kill' in actions and actions['kill'] == werewolf_target:
                        werewolf_killer = player_name
                        break
                
                if werewolf_killer:
                    self.reveal_death_note_on_kill(game, werewolf_killer, werewolf_target)
                
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
            target_role = game['players'][witch_poison_target]['role'].value if isinstance(game['players'][witch_poison_target]['role'], Role) else game['players'][witch_poison_target]['role']
            print(f"DEBUG: Witch poison killing {witch_poison_target} (role: {target_role})")
            game['players'][witch_poison_target]['alive'] = False
            eliminated_info = {
                'name': witch_poison_target,
                'cause': 'witch_poison',
                'day': game['day_count'],
                'role': target_role
            }
            game['eliminated_players'].append(eliminated_info)
            elimination_stories.append(self._generate_death_story(witch_poison_target, 'witch_poison', target_role))
            
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
        
        # Combine all elimination stories
        if elimination_stories:
            game['last_elimination'] = '\n\n'.join(elimination_stories)
    
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
                game['last_elimination'] = self._generate_death_story(eliminated, 'voted_out', eliminated_player['role'], max_votes)
                
                # Ajouter à l'historique avec nom de rôle en français et gestion singulier/pluriel
                role_names = {
                    'villager': 'Villageois',
                    'werewolf': 'Loup-Garou',
                    'seer': 'Voyant',
                    'witch': 'Sorcière',
                    'guard': 'Garde',
                    'bodyguard': 'Garde',
                    'hunter': 'Chasseur'
                }
                role_display = role_names.get(eliminated_info['role'], eliminated_info['role'])
                vote_text = "vote" if max_votes == 1 else "votes"
                
                game['game_history'].append({
                    'type': 'elimination',
                    'phase': 'day',
                    'day': game['day_count'],
                    'player_name': eliminated,  # Changé de 'player' à 'player_name' pour cohérence
                    'cause': 'voted_out',
                    'role': eliminated_info['role'],
                    'votes': max_votes,
                    'description': f"{eliminated} a été éliminé par le village ({max_votes} {vote_text})\nRôle : {role_display}"
                })
                
                # Hunter revenge
                if game['players'][eliminated]['role'] == Role.HUNTER:
                    # Hunter can kill someone when eliminated
                    # This would need additional UI handling
                    pass
                
                return eliminated
        
        return None
    
    def cast_vote(self, game_id, player_name, target):
        """Cast a vote during day phase or voting phase - permet de changer de vote"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        # Permettre le vote pendant DAY et VOTING phases
        if game['phase'] not in [Phase.DAY, Phase.VOTING]:
            return False, "Votes seulement disponibles pendant le jour ou la phase de vote"
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        player = game['players'][player_name]
        
        if not player['alive']:
            return False, "Dead players cannot vote"
        
        if target not in game['players'] or not game['players'][target]['alive']:
            return False, "Invalid vote target"
        
        if target == player_name:
            return False, "Vous ne pouvez pas voter contre vous-même"
        
        # Permettre de changer de vote
        previous_vote = player.get('vote_target')
        player['vote_target'] = target
        player['has_voted'] = True
        
        # Pas de message de feedback - rester discret
        return True, ""
    
    def _check_game_end(self, game):
        """Check if the game has ended"""
        alive_players = [p for p in game['players'].values() if p['alive']]
        alive_werewolves = [p for p in alive_players if p['role'] == Role.WEREWOLF]
        alive_villagers = [p for p in alive_players if p['role'] != Role.WEREWOLF]
        
        if len(alive_werewolves) == 0:
            game['winner'] = 'villagers'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            game['game_history'].append({
                'type': 'game_end',
                'phase': 'end',
                'day': game['day_count'],
                'winner': 'villagers',
                'description': '🎉 Victoire du Village ! Tous les loups-garous ont été éliminés.'
            })
            return True
        elif len(alive_werewolves) >= len(alive_villagers):
            game['winner'] = 'werewolves'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            game['game_history'].append({
                'type': 'game_end',
                'phase': 'end',
                'day': game['day_count'],
                'winner': 'werewolves',
                'description': '🐺 Victoire des Loups-Garous ! Ils dominent le village.'
            })
            return True
        
        return False
    
    def add_chat_message(self, game_id, player_name, message, channel=ChatChannel.PUBLIC):
        """Add a chat message to the appropriate channel"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        player = game['players'][player_name]
        
        # Vérifier les permissions de chat selon la phase et le canal
        if not self._can_send_message(game, player, channel):
            return False, "Chat non autorisé dans ce canal"
        
        chat_message = {
            'player': player_name,
            'player_name': player_name,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'day': game.get('day_count', 0),
            'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
            'channel': channel.value if isinstance(channel, ChatChannel) else channel
        }
        
        # Ajouter au bon canal
        if channel == ChatChannel.PUBLIC:
            game['chat_messages'].append(chat_message)
        elif channel == ChatChannel.MAFIA:
            game['mafia_chat'].append(chat_message)
        elif channel == ChatChannel.TRIAD:
            game['triad_chat'].append(chat_message)
        elif channel == ChatChannel.DEAD:
            game['dead_chat'].append(chat_message)
        elif channel == ChatChannel.PRIVATE:
            game['private_messages'].append(chat_message)
        
        return True, "Message ajouté"
    
    def _can_send_message(self, game, player, channel):
        """Vérifie si un joueur peut envoyer un message dans un canal"""
        player_role = player['role']
        player_alive = player['alive']
        current_phase = game['phase']
        
        if channel == ChatChannel.PUBLIC:
            # Chat public : seulement pendant le jour et si vivant
            return current_phase in [Phase.DAY, Phase.VOTING, Phase.TRIAL] and player_alive
            
        elif channel == ChatChannel.MAFIA:
            # Chat mafia : seulement la nuit, si mafia et vivant
            return (current_phase == Phase.NIGHT and 
                   player_role == Role.WEREWOLF and 
                   player_alive and 
                   game.get('night_chat_enabled', True))
            
        elif channel == ChatChannel.TRIAD:
            # Chat triad : seulement la nuit, si triad et vivant
            # Note: Pas de rôles triad implémentés encore
            return False
            
        elif channel == ChatChannel.DEAD:
            # Chat des morts : seulement si mort
            return not player_alive
            
        elif channel == ChatChannel.PRIVATE:
            # Messages privés : toujours autorisés si vivant
            return player_alive
            
        return False
    
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
        
        # Pas d'actions pendant les transitions
        if game['phase'] == Phase.TRANSITION:
            return []
        
        actions = []
        
        # Get alive players (potential targets)
        alive_players = [name for name, p in game['players'].items() if p['alive']]
        alive_others = [name for name in alive_players if name != player_name]
        
        if game['phase'] == Phase.NIGHT:
            if player['role'] == Role.WEREWOLF and not player.get('night_action_used', False):
                # Werewolves can kill villagers
                werewolf_targets = [name for name, p in game['players'].items() 
                                  if p['alive'] and p['role'] != Role.WEREWOLF and name != player_name]
                if werewolf_targets:
                    actions.append({
                        'type': 'kill',
                        'description': 'Choisir une victime à éliminer',
                        'targets': werewolf_targets
                    })
            
            elif player['role'] == Role.SEER and not player.get('night_action_used', False):
                # Seer can investigate any alive player except themselves
                if alive_others:
                    actions.append({
                        'type': 'investigate',
                        'description': 'Découvrir le rôle d\'un joueur',
                        'targets': alive_others
                    })
            
            elif player['role'] == Role.GUARD and not player.get('night_action_used', False):
                # Guard can protect any alive player except themselves (and not the same person twice in a row)
                guard_targets = [name for name in alive_others if name != player.get('last_protected')]
                if guard_targets:
                    actions.append({
                        'type': 'protect',
                        'description': 'Protéger un joueur des attaques',
                        'targets': guard_targets
                    })
            
            elif player['role'] == Role.WITCH:
                witch_actions = []
                
                if not player.get('witch_heal_used', False):
                    witch_actions.append({
                        'type': 'heal',
                        'description': 'Utiliser la potion de guérison (1 fois)',
                        'targets': []  # No target needed, will heal the night victim
                    })
                
                if not player.get('witch_poison_used', False) and alive_others:
                    witch_actions.append({
                        'type': 'poison',
                        'description': 'Empoisonner un joueur (1 fois)',
                        'targets': alive_others
                    })
                
                actions.extend(witch_actions)
            
            # 🆕 CHAPITRE 2 - ACTIONS INVESTIGATIVES
            elif player['role'] == Role.SHERIFF and not player.get('night_action_used', False):
                # Sheriff peut investiguer n'importe qui d'autre
                if alive_others:
                    actions.append({
                        'type': 'investigate',
                        'description': 'Investiguer un suspect (Résultat: Suspect/Non Suspect)',
                        'targets': alive_others
                    })
            
            elif player['role'] == Role.INVESTIGATOR and not player.get('night_action_used', False):
                # Investigator peut investiguer n'importe qui d'autre
                if alive_others:
                    actions.append({
                        'type': 'investigate',
                        'description': 'Analyser un joueur (Indices sur le type de rôle)',
                        'targets': alive_others
                    })
        
        elif game['phase'] == Phase.DAY:
            # Check if we're in the voting period (last 40 seconds)
            can_vote = False
            if game['phase_start_time'] and game['phase_duration']:
                elapsed = (datetime.now() - game['phase_start_time']).total_seconds()
                remaining_time = max(0, game['phase_duration'] - elapsed)
                can_vote = remaining_time <= 40
            
            if can_vote and not player.get('has_voted', False):
                vote_targets = [name for name in alive_others]
                if vote_targets:
                    actions.append({
                        'type': 'vote',
                        'description': 'Voter pour lyncher un suspect',
                        'targets': vote_targets
                    })
        
        elif game['phase'] == Phase.VOTING:
            # Always allow voting during voting phase
            if not player.get('has_voted', False):
                vote_targets = [name for name in alive_others]
                if vote_targets:
                    actions.append({
                        'type': 'vote',
                        'description': 'Voter pour lyncher un suspect',
                        'targets': vote_targets
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
    
    def _generate_death_story(self, player_name, cause, role, votes=None):
        """Generate a narrative death story based on cause and role"""
        role_str = role.value if hasattr(role, 'value') else str(role)
        
        stories = {
            'werewolf_kill': {
                'villager': [
                    f"🌙 {player_name} a été retrouvé(e) ce matin, déchiqueté(e) par les griffes acérées des loups-garous. Les traces de sang mènent vers la forêt sombre...",
                    f"💀 Le corps mutilé de {player_name} gît dans la rue principale. Les habitants frissonnent en voyant les marques de crocs sur le cadavre.",
                    f"🩸 {player_name} n'est jamais rentré(e) chez lui/elle cette nuit. On l'a retrouvé(e) à l'orée du village, victime de la férocité des créatures nocturnes."
                ],
                'seer': [
                    f"🔮 {player_name}, le/la voyant(e) du village, a été éliminé(e) par les loups-garous. Ses visions s'éteignent avec elle dans un dernier souffle sanglant.",
                    f"👁️ Les loups-garous ont traqué {player_name} toute la nuit. Le/la voyant(e) a payé le prix de ses révélations par sa vie.",
                    f"🌟 {player_name} repose désormais en paix, mais ses secrets sont morts avec lui/elle. Les loups ont fait taire l'oracle du village."
                ],
                'witch': [
                    f"🧪 {player_name}, la sorcière aux potions magiques, a été découverte morte dans sa cabane. Ses fioles brisées jonchent le sol ensanglanté.",
                    f"⚗️ Les loups-garous ont dévasté l'antre de {player_name}. La sorcière n'a pas eu le temps d'utiliser ses dernières potions pour se défendre.",
                    f"🍃 {player_name} gît parmi ses herbes et ses grimoires. Les créatures de la nuit ont mis fin aux sortilèges de la sorcière."
                ],
                'bodyguard': [
                    f"🛡️ {player_name}, le/la garde du village, est tombé(e) en défendant les innocents. Son sacrifice ne sera pas oublié.",
                    f"⚔️ Malgré sa bravoure, {player_name} n'a pas pu résister à la meute. Le/la protecteur/protectrice du village repose maintenant en paix.",
                    f"🏰 {player_name} a livré son dernier combat cette nuit. Le/la garde est mort(e) l'épée à la main, face aux loups-garous."
                ],
                'hunter': [
                    f"🏹 {player_name}, le/la chasseur/chasseuse expérimenté(e), a été pris(e) par surprise par les loups. Même les meilleurs traqueurs peuvent devenir proies.",
                    f"🎯 Les loups-garous ont eu raison de {player_name} cette nuit. Le/la chasseur/chasseuse n'a pas eu le temps de tirer sa dernière flèche.",
                    f"🦌 {player_name} traquait les créatures nocturnes, mais c'est lui/elle qui a été traqué(e). La chasse s'est retournée contre le/la chasseur/chasseuse."
                ],
                'werewolf': [
                    f"🐺 {player_name} a été éliminé(e) par ses propres congénères. La meute n'épargne personne, pas même les leurs.",
                    f"🌕 Une lutte fratricide a eu lieu cette nuit. {player_name} est tombé(e) sous les crocs de sa propre meute.",
                    f"⚡ {player_name} a payé le prix de la trahison. Les loups-garous ne tolèrent aucune faiblesse dans leurs rangs."
                ]
            },
            'voted_out': {
                'villager': [
                    f"⚖️ {player_name} a été lynché(e) par la foule en colère ({votes} votes). Un innocent de plus tombe sous la justice aveugle du village.",
                    f"🔥 Les villageois ont traîné {player_name} sur la place publique. Le bûcher s'allume, emportant un innocent ({votes} votes).",
                    f"👥 {player_name} supplie en vain son innocence. La majorité a parlé ({votes} votes), et le village a perdu un de ses membres."
                ],
                'seer': [
                    f"🔮 {player_name}, le/la voyant(e), a été condamné(e) par ceux qu'il/elle tentait de protéger ({votes} votes). Ses visions s'éteignent avec sa vie.",
                    f"👁️ Le village a fait une erreur fatale en éliminant {player_name} ({votes} votes). L'oracle qui voyait la vérité ne parlera plus.",
                    f"💫 {player_name} emporte ses secrets dans la tombe. Le/la voyant(e) a été sacrifié(e) par la peur et l'ignorance ({votes} votes)."
                ],
                'witch': [
                    f"🧪 {player_name}, accusée de sorcellerie, a ironiquement été brûlée par le village ({votes} votes). Ses potions n'ont pas pu la sauver de la superstition.",
                    f"⚗️ La vraie sorcière {player_name} a été découverte et exécutée ({votes} votes). Ses dernières potions se brisent sur les pavés.",
                    f"🔥 {player_name} périt dans les flammes de la justice populaire ({votes} votes). La sorcière paie le prix de ses secrets."
                ],
                'bodyguard': [
                    f"🛡️ {player_name}, le/la protecteur/protectrice du village, a été trahi(e) par ceux qu'il/elle défendait ({votes} votes). L'ironie du destin frappe fort.",
                    f"⚔️ Le village a perdu son meilleur défenseur en éliminant {player_name} ({votes} votes). Qui les protégera maintenant ?",
                    f"🏰 {player_name} tombe sous les accusations. Le/la garde qui veillait sur tous est devenu(e) la cible de tous ({votes} votes)."
                ],
                'hunter': [
                    f"🏹 {player_name}, le/la chasseur/chasseuse, a été pris(e) au piège de la suspicion ({votes} votes). Même les traqueurs peuvent être traqués.",
                    f"🎯 Le village a éliminé {player_name} ({votes} votes). Le/la chasseur/chasseuse expérimenté(e) n'a pas vu venir cette chasse à l'homme.",
                    f"🦌 {player_name} a été abattu(e) par la foule ({votes} votes). Le/la chasseur/chasseuse devient le gibier."
                ],
                'werewolf': [
                    f"🐺 {player_name} a été démasqué(e) et lynché(e) par le village ({votes} votes) ! La bête immonde paie enfin pour ses crimes nocturnes.",
                    f"🌕 Justice est rendue ! {player_name}, le/la loup-garou, a été éliminé(e) par la volonté du peuple ({votes} votes).",
                    f"⚡ {player_name} révèle sa vraie nature avant de mourir. Le village a réussi à éliminer une créature maléfique ({votes} votes) !"
                ]
            },
            'witch_poison': {
                'default': [
                    f"☠️ {player_name} a été empoisonné(e) par la sorcière. Le poison mortel a fait son œuvre dans la nuit.",
                    f"🧪 {player_name} s'effondre, victime d'une potion mortelle. La sorcière a frappé silencieusement.",
                    f"💀 {player_name} agonise, le visage déformé par le poison. La vengeance de la sorcière est terrible."
                ]
            }
        }
        
        # Sélectionner une histoire aléatoire
        if cause in stories and role_str in stories[cause]:
            return random.choice(stories[cause][role_str])
        elif cause in stories and 'default' in stories[cause]:
            return random.choice(stories[cause]['default'])
        else:
            # Fallback
            return f"{player_name} a été éliminé(e)."

    # 🆕 ==================== SYSTÈME DE PROCÈS ====================
    
    def _check_for_trial(self, game):
        """Vérifie si un joueur doit être mis en procès selon le type de vote"""
        if not game['day_voting_enabled']:
            return None
            
        alive_players = [p for p in game['players'].values() if p['alive']]
        total_alive = len(alive_players)
        
        if total_alive == 0:
            return None
            
        # Compter les votes pour chaque joueur
        vote_counts = {}
        for player_name, player in game['players'].items():
            if player['alive'] and player.get('vote_target'):
                target = player['vote_target']
                vote_counts[target] = vote_counts.get(target, 0) + 1
        
        vote_type = game['vote_type']
        threshold = int(total_alive * game['lynch_threshold'])
        
        if vote_type in [VoteType.MAJORITY, VoteType.MAJORITY_TRIAL]:
            # Vote majoritaire : il faut 51%+ des votes
            for player_name, votes in vote_counts.items():
                if votes >= threshold:
                    if vote_type == VoteType.MAJORITY:
                        # Lynch direct sans procès
                        return {'player': player_name, 'votes': votes, 'direct_lynch': True}
                    else:
                        # Procès requis
                        return {'player': player_name, 'votes': votes, 'direct_lynch': False}
                        
        elif vote_type in [VoteType.BALLOT, VoteType.BALLOT_TRIAL]:
            # Vote secret : celui avec le plus de votes
            if vote_counts:
                max_votes = max(vote_counts.values())
                candidates = [name for name, votes in vote_counts.items() if votes == max_votes]
                
                if len(candidates) == 1:  # Pas d'égalité
                    player_name = candidates[0]
                    if vote_type == VoteType.BALLOT:
                        # Lynch direct sans procès
                        return {'player': player_name, 'votes': max_votes, 'direct_lynch': True}
                    else:
                        # Procès requis
                        return {'player': player_name, 'votes': max_votes, 'direct_lynch': False}
                        
        return None
        
    def _start_trial(self, game, accusation_info):
        """Démarre le procès ou lynch direct"""
        player_name = accusation_info['player']
        votes = accusation_info['votes']
        direct_lynch = accusation_info['direct_lynch']
        
        if direct_lynch:
            # Lynch direct sans procès
            game['accused_player'] = player_name
            return self._execute_accused(game, direct=True)
        else:
            # Procès avec défense et vote
            game['phase'] = Phase.TRIAL
            game['accused_player'] = player_name
            
            # 🐛 FIX BUG-001: Reset complet du timer à chaque nouveau procès
            current_time = datetime.now()
            game['phase_start_time'] = current_time
            game['phase_duration'] = game['trial_defense_time'] + game['trial_voting_time']
            game['day_voting_enabled'] = False  # Désactiver votes jour
            
            # Reset trial votes complètement
            game['trial_votes'] = {}
            for player in game['players'].values():
                player['trial_vote'] = None
                
            print(f"Nouveau procès démarré contre {player_name} à {current_time.isoformat()}")
                
            # Ajouter à l'historique
            game['trial_history'].append({
                'accused': player_name,
                'votes_to_trial': votes,
                'day': game['day_count'],
                'timestamp': datetime.now().isoformat()
            })
            
            game['game_history'].append({
                'type': 'trial_start',
                'phase': 'trial',
                'day': game['day_count'],
                'accused': player_name,
                'votes': votes,
                'description': f"{player_name} est mis en procès avec {votes} votes"
            })
            
            return True, f"{player_name} est mis en procès ! Temps de défense puis vote innocent/coupable."
            
    def _process_trial_votes(self, game):
        """Traite les votes innocent/coupable du procès"""
        accused = game['accused_player']
        if not accused:
            return False, "Pas de joueur en procès"
            
        # Compter les votes innocent/coupable
        guilty_votes = 0
        innocent_votes = 0
        total_voters = 0
        
        for player_name, player in game['players'].items():
            if player['alive'] and player_name != accused:  # L'accusé ne vote pas
                trial_vote = player.get('trial_vote')
                if trial_vote == TrialVerdict.GUILTY:
                    guilty_votes += 1
                elif trial_vote == TrialVerdict.INNOCENT:
                    innocent_votes += 1
                total_voters += 1
                
        # Déterminer le verdict (majorité requise pour condamner)
        required_for_guilty = total_voters // 2 + 1
        
        if guilty_votes >= required_for_guilty:
            # Coupable - Exécution
            game['phase'] = Phase.LYNCHING
            game['phase_start_time'] = datetime.now()
            game['phase_duration'] = 10  # 10 secondes pour montrer l'exécution
            
            verdict = "COUPABLE"
        else:
            # Innocent - Retour au jour ou fin de journée
            verdict = "INNOCENT"
            game['accused_player'] = None
            
            # Vérifier s'il reste du temps de jour
            elapsed_day_time = (datetime.now() - game['phase_start_time']).total_seconds()
            remaining_day_time = max(0, 120 - elapsed_day_time)  # 2min de jour par défaut
            
            if remaining_day_time > 30:  # S'il reste plus de 30 sec
                # Retour au jour
                game['phase'] = Phase.DAY
                game['phase_duration'] = remaining_day_time
                game['day_voting_enabled'] = True
            else:
                # Fin de journée directe
                self._process_day_end(game)
                
        # Enregistrer le verdict
        game['game_history'].append({
            'type': 'trial_verdict',
            'phase': 'trial',
            'day': game['day_count'],
            'accused': accused,
            'verdict': verdict,
            'guilty_votes': guilty_votes,
            'innocent_votes': innocent_votes,
            'description': f"{accused} jugé {verdict} ({guilty_votes} coupable, {innocent_votes} innocent)"
        })
        
        return True, f"Verdict : {verdict} ({guilty_votes} coupable, {innocent_votes} innocent)"
        
    def _execute_accused(self, game, direct=False):
        """Exécute le joueur accusé"""
        accused = game['accused_player']
        if not accused or accused not in game['players']:
            return False, "Joueur accusé invalide"
            
        accused_player = game['players'][accused]
        accused_role = accused_player['role']
        
        # Éliminer le joueur
        accused_player['alive'] = False
        
        # Ajouter aux éliminés
        eliminated_info = {
            'name': accused,
            'cause': 'lynch_direct' if direct else 'lynch_trial',
            'day': game['day_count'],
            'role': accused_role.value if hasattr(accused_role, 'value') else str(accused_role)
        }
        game['eliminated_players'].append(eliminated_info)
        
        # 🆕 Révéler testament automatiquement à l'exécution
        self.reveal_will_on_death(game, accused)
        
        # Générer histoire de mort
        execution_story = self._generate_death_story(accused, 'voted_out', accused_role)
        game['last_elimination'] = execution_story
        
        # Historique
        game['game_history'].append({
            'type': 'execution',
            'phase': 'lynching' if not direct else 'day',
            'day': game['day_count'],
            'player': accused,
            'cause': 'lynch_direct' if direct else 'lynch_trial',
            'role': eliminated_info['role'],
            'description': f"{accused} ({eliminated_info['role']}) a été exécuté par le village"
        })
        
        # Reset accused
        game['accused_player'] = None
        
        if direct:
            # Lynch direct, aller aux résultats de jour
            game['phase'] = Phase.TRANSITION
            game['phase_start_time'] = datetime.now()
            game['phase_duration'] = 15
            game['transition_type'] = 'day_results'
            
        return True, f"{accused} a été exécuté par le village."
        
    def _process_day_end(self, game):
        """Gère la fin de journée sans procès ni lynch"""
        game['phase'] = Phase.TRANSITION
        game['phase_start_time'] = datetime.now()
        game['phase_duration'] = 15
        game['transition_type'] = 'day_results'
        game['last_elimination'] = "Aucune exécution aujourd'hui. Le village n'a pas pu se mettre d'accord."
        
    def cast_trial_vote(self, game_id, player_name, verdict):
        """Vote innocent ou coupable pendant un procès"""
        if game_id not in self.games:
            return False, "Game not found"
            
        game = self.games[game_id]
        
        if game['phase'] != Phase.TRIAL:
            return False, "Pas en phase de procès"
            
        # 🐛 FIX BUG-010: Vérifier que le procès n'a pas expiré
        if game.get('phase_start_time'):
            elapsed_time = (datetime.now() - game['phase_start_time']).total_seconds()
            if elapsed_time > game.get('phase_duration', 60):
                return False, "Temps de procès expiré - vote non comptabilisé"
            
        if player_name not in game['players']:
            return False, "Player not found"
            
        player = game['players'][player_name]
        
        if not player['alive']:
            return False, "Les morts ne peuvent pas voter"
            
        if player_name == game['accused_player']:
            return False, "L'accusé ne peut pas voter à son propre procès"
            
        if verdict not in [TrialVerdict.GUILTY, TrialVerdict.INNOCENT]:
            return False, "Verdict invalide"
            
        # Vérifier que le joueur n'a pas déjà voté
        if player_name in game.get('trial_votes', {}):
            return False, "Vous avez déjà voté"
            
        # Enregistrer le vote
        player['trial_vote'] = verdict
        game['trial_votes'][player_name] = verdict
        
        verdict_fr = "COUPABLE" if verdict == TrialVerdict.GUILTY else "INNOCENT"
        print(f"{player_name} a voté {verdict_fr} dans le procès")
        return True, f"Vous avez voté {verdict_fr}"

    def get_chat_messages(self, game_id, player_name):
        """Récupère tous les messages de chat accessibles au joueur"""
        if game_id not in self.games:
            return {}
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return {}
        
        player = game['players'][player_name]
        accessible_messages = {}
        
        # Chat public - toujours accessible
        accessible_messages['public'] = game['chat_messages']
        
        # Chat mafia - seulement si mafia
        if player['role'] == Role.WEREWOLF:
            accessible_messages['mafia'] = game['mafia_chat']
        
        # Chat des morts - seulement si mort
        if not player['alive']:
            accessible_messages['dead'] = game['dead_chat']
        
        # Messages privés - toujours accessibles
        # Filtrer pour ne montrer que ceux destinés au joueur
        player_private_messages = [
            msg for msg in game['private_messages']
            if msg.get('recipient') == player_name or msg.get('sender') == player_name
        ]
        accessible_messages['private'] = player_private_messages
        
        return accessible_messages
    
    def send_private_message(self, game_id, sender, recipient, message):
        """Envoie un message privé avec notification publique"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if sender not in game['players'] or recipient not in game['players']:
            return False, "Joueur non trouvé"
        
        sender_player = game['players'][sender]
        recipient_player = game['players'][recipient]
        
        # Vérifier que les deux joueurs sont vivants
        if not sender_player['alive'] or not recipient_player['alive']:
            return False, "Les morts ne peuvent pas envoyer de MP"
        
        # Créer le message privé
        private_message = {
            'sender': sender,
            'recipient': recipient,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'day': game.get('day_count', 0),
            'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
            'channel': 'private'
        }
        
        game['private_messages'].append(private_message)
        
        # Notification publique selon les règles SC2 Mafia
        notification = {
            'player': 'SYSTEM',
            'player_name': 'SYSTEM',
            'message': f"{sender} a envoyé un message privé à {recipient}",
            'timestamp': datetime.now().isoformat(),
            'day': game.get('day_count', 0),
            'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
            'channel': 'public',
            'is_notification': True
        }
        
        game['chat_messages'].append(notification)
        
        return True, "Message privé envoyé"
    
    def get_available_chat_channels(self, game_id, player_name):
        """Retourne les canaux de chat disponibles pour un joueur"""
        if game_id not in self.games:
            return []
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return []
        
        player = game['players'][player_name]
        channels = []
        
        # Canal public
        if self._can_send_message(game, player, ChatChannel.PUBLIC):
            channels.append({
                'id': 'public',
                'name': 'Village',
                'description': 'Chat public du village',
                'color': '#3b82f6'
            })
        
        # Canal mafia
        if self._can_send_message(game, player, ChatChannel.MAFIA):
            channels.append({
                'id': 'mafia',
                'name': 'Meute',
                'description': 'Chat privé des loups-garous',
                'color': '#ef4444'
            })
        
        # Canal des morts
        if self._can_send_message(game, player, ChatChannel.DEAD):
            channels.append({
                'id': 'dead',
                'name': 'Outre-tombe',
                'description': 'Chat des esprits',
                'color': '#6b7280'
            })
        
        # Messages privés
        if self._can_send_message(game, player, ChatChannel.PRIVATE):
            channels.append({
                'id': 'private',
                'name': 'Messages Privés',
                'description': 'Conversations secrètes',
                'color': '#8b5cf6'
            })
        
        return channels
    
    # 🆕 ==================== SYSTÈME DE TESTAMENT ====================
    
    def save_last_will(self, game_id, player_name, last_will):
        """Sauvegarde le testament d'un joueur"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return False, "Player not found"
        
        player = game['players'][player_name]
        
        # Seuls les vivants peuvent modifier leur testament
        if not player['alive']:
            return False, "Les morts ne peuvent pas modifier leur testament"
        
        # Limiter la taille du testament
        if len(last_will) > 1000:
            return False, "Testament trop long (max 1000 caractères)"
        
        game['last_wills'][player_name] = {
            'content': last_will,
            'last_updated': datetime.now().isoformat(),
            'day': game.get('day_count', 1)
        }
        
        # Sauvegarder aussi dans le joueur pour compatibilité
        player['last_will'] = last_will
        
        return True, "Testament sauvegardé"
    
    def get_player_will(self, game_id, player_name):
        """Récupère le testament d'un joueur"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return None
        
        will_data = game['last_wills'].get(player_name)
        if will_data:
            return will_data
        
        # Fallback pour compatibilité
        player = game['players'][player_name]
        if player.get('last_will'):
            return {
                'content': player['last_will'],
                'last_updated': None,
                'day': game.get('day_count', 1)
            }
        
        return None
    
    def reveal_will_on_death(self, game, player_name):
        """Révèle automatiquement le testament d'un joueur mort"""
        # 🐛 FIX BUG-005: Vérifier si le testament a déjà été révélé
        already_revealed = any(will['player'] == player_name for will in game['revealed_wills'])
        if already_revealed:
            print(f"Testament de {player_name} déjà révélé, skip duplication")
            return False
            
        will_data = self.get_player_will(game['id'], player_name)
        
        if will_data and will_data['content'].strip():
            revealed_will = {
                'player': player_name,
                'content': will_data['content'],
                'death_day': game.get('day_count', 1),
                'death_time': datetime.now().isoformat(),
                'cause': 'death_revelation'
            }
            
            game['revealed_wills'].append(revealed_will)
            
            # Ajouter notification dans le chat public
            will_notification = {
                'player': 'SYSTEM',
                'player_name': 'SYSTEM',
                'message': f"📜 Testament de {player_name} révélé : \"{will_data['content'][:100]}{'...' if len(will_data['content']) > 100 else ''}\"",
                'timestamp': datetime.now().isoformat(),
                'day': game.get('day_count', 0),
                'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
                'channel': 'public',
                'is_will_reveal': True,
                'full_will': will_data['content']
            }
            
            game['chat_messages'].append(will_notification)
            
            print(f"Testament de {player_name} révélé avec succès")
            return True
        
        return False
    
    # 🆕 ==================== SYSTÈME DE NOTES DE MORT ====================
    
    def save_death_note(self, game_id, killer_name, victim_name, death_note):
        """Sauvegarde une note de mort d'un tueur"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if killer_name not in game['players']:
            return False, "Killer not found"
        
        killer = game['players'][killer_name]
        
        # Vérifier que le joueur peut laisser des notes de mort
        if not self._can_leave_death_note(killer):
            return False, "Vous ne pouvez pas laisser de notes de mort"
        
        # Limiter la taille de la note
        if len(death_note) > 300:
            return False, "Note de mort trop longue (max 300 caractères)"
        
        # Créer la clé de la note
        note_key = f"{killer_name}_{victim_name}_{game.get('day_count', 1)}"
        
        game['death_notes'][note_key] = {
            'killer': killer_name,
            'victim': victim_name,
            'content': death_note,
            'day': game.get('day_count', 1),
            'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
            'timestamp': datetime.now().isoformat()
        }
        
        return True, "Note de mort sauvegardée"
    
    def _can_leave_death_note(self, player):
        """Vérifie si un joueur peut laisser des notes de mort"""
        if not player['alive']:
            return False
        
        # Seuls certains rôles peuvent laisser des notes de mort
        killer_roles = [Role.WEREWOLF]  # À étendre avec Serial Killer, etc.
        
        return player['role'] in killer_roles
    
    def reveal_death_note_on_kill(self, game, killer_name, victim_name):
        """Révèle la note de mort quand une victime est tuée"""
        note_key = f"{killer_name}_{victim_name}_{game.get('day_count', 1)}"
        
        death_note_data = game['death_notes'].get(note_key)
        
        if death_note_data and death_note_data['content'].strip():
            # Ajouter la note à l'histoire des révélations
            death_note_reveal = {
                'killer': killer_name,
                'victim': victim_name,
                'content': death_note_data['content'],
                'day': game.get('day_count', 1),
                'timestamp': datetime.now().isoformat(),
                'revealed': True
            }
            
            # Ajouter notification dans le chat public
            note_notification = {
                'player': 'SYSTEM',
                'player_name': 'SYSTEM', 
                'message': f"🩸 Note trouvée sur le corps de {victim_name} : \"{death_note_data['content']}\"",
                'timestamp': datetime.now().isoformat(),
                'day': game.get('day_count', 0),
                'phase': game['phase'].value if isinstance(game['phase'], Phase) else game['phase'],
                'channel': 'public',
                'is_death_note': True,
                'killer_role': 'unknown'  # Ne pas révéler l'identité du tueur
            }
            
            game['chat_messages'].append(note_notification)
            
            return True
        
        return False
    
    def get_available_death_note_targets(self, game_id, player_name):
        """Retourne les cibles possibles pour une note de mort"""
        if game_id not in self.games:
            return []
        
        game = self.games[game_id]
        
        if player_name not in game['players']:
            return []
        
        player = game['players'][player_name]
        
        if not self._can_leave_death_note(player):
            return []
        
        # Retourner tous les joueurs vivants sauf le tueur
        targets = []
        for name, target_player in game['players'].items():
            if target_player['alive'] and name != player_name:
                targets.append({
                    'name': name,
                    'role': target_player['role'].value if hasattr(target_player['role'], 'value') else str(target_player['role'])
                })
        
        return targets
    
    def get_revealed_wills(self, game_id):
        """Récupère tous les testaments révélés"""
        if game_id not in self.games:
            return []
        
        return self.games[game_id].get('revealed_wills', [])
    
    def get_death_notes_history(self, game_id):
        """Récupère l'historique des notes de mort"""
        if game_id not in self.games:
            return []
        
        game = self.games[game_id]
        
        # Filtrer seulement les notes révélées (sur des victimes mortes)
        revealed_notes = []
        for note_data in game['death_notes'].values():
            victim_name = note_data['victim']
            if victim_name in game['players'] and not game['players'][victim_name]['alive']:
                revealed_notes.append(note_data)
        
        return revealed_notes
    
    # 🆕 ==================== SYSTÈME D'INVESTIGATION ====================
    
    def _get_sheriff_result(self, investigator_role, target_role):
        """Détermine le résultat d'investigation du Sheriff"""
        # Rôles suspects (Evil/Mafia)
        suspicious_roles = [Role.WEREWOLF]  # À étendre avec Mafia, Serial Killer, etc.
        
        # Rôles immunisés (comme Godfather dans SC2 Mafia)
        immune_roles = []  # À étendre avec Godfather quand implémenté
        
        if target_role in immune_roles:
            return SheriffResult.NOT_SUSPICIOUS  # Immunité
        elif target_role in suspicious_roles:
            return SheriffResult.SUSPICIOUS
        else:
            return SheriffResult.NOT_SUSPICIOUS
    
    def _get_investigator_group(self, target_role):
        """Détermine le groupe d'investigation pour l'Investigator"""
        # Mapping rôles vers groupes d'investigation
        role_groups = {
            Role.GUARD: InvestigationGroup.PROTECTORS,
            Role.SHERIFF: InvestigationGroup.INVESTIGATORS,
            Role.INVESTIGATOR: InvestigationGroup.INVESTIGATORS,
            Role.SEER: InvestigationGroup.INVESTIGATORS,
            Role.WEREWOLF: InvestigationGroup.KILLERS,
            Role.HUNTER: InvestigationGroup.KILLERS,
            Role.VILLAGER: InvestigationGroup.SUPPORT,
            Role.WITCH: InvestigationGroup.WITCHES
        }
        
        return role_groups.get(target_role, InvestigationGroup.SUPPORT)
    
    def _get_investigation_group_message(self, group):
        """Retourne le message d'investigation pour un groupe"""
        group_messages = {
            InvestigationGroup.PROTECTORS: "Votre cible pourrait être un Bodyguard, Lookout ou Spy.",
            InvestigationGroup.INVESTIGATORS: "Votre cible pourrait être un Sheriff, Investigator ou Detective.",
            InvestigationGroup.KILLERS: "Votre cible pourrait être un Vigilante, Veteran ou Werewolf.",
            InvestigationGroup.SUPPORT: "Votre cible pourrait être un Citizen, Mayor ou Mason.",
            InvestigationGroup.WITCHES: "Votre cible pourrait être une Witch ou Witch Doctor.",
            InvestigationGroup.NEUTRALS: "Votre cible pourrait être un Survivor, Amnesiac ou Judge."
        }
        
        return group_messages.get(group, "Votre cible a un rôle indéterminé.")
    
    def perform_sheriff_investigation(self, game_id, sheriff_name, target_name):
        """Effectue une investigation Sheriff"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if sheriff_name not in game['players']:
            return False, "Sheriff not found"
        
        sheriff = game['players'][sheriff_name]
        
        # Vérifications de base
        if sheriff['role'] != Role.SHERIFF:
            return False, "Seul le Sheriff peut faire des investigations"
        
        if not sheriff['alive']:
            return False, "Les morts ne peuvent pas investiguer"
        
        if game['phase'] != Phase.NIGHT:
            return False, "Les investigations se font la nuit"
        
        if target_name not in game['players']:
            return False, "Cible non trouvée"
        
        target = game['players'][target_name]
        
        if not target['alive']:
            return False, "Impossible d'investiguer un mort"
        
        if target_name == sheriff_name:
            return False, "Vous ne pouvez pas vous investiguer vous-même"
        
        # Effectuer l'investigation
        result = self._get_sheriff_result(Role.SHERIFF, target['role'])
        
        # Stocker le résultat
        if sheriff_name not in game['investigation_results']:
            game['investigation_results'][sheriff_name] = []
        
        investigation_data = {
            'investigator': sheriff_name,
            'target': target_name,
            'result': result.value,
            'result_type': 'sheriff',
            'night': game.get('day_count', 1),
            'timestamp': datetime.now().isoformat()
        }
        
        game['investigation_results'][sheriff_name].append(investigation_data)
        game['investigation_history'].append(investigation_data)
        
        # Message pour le Sheriff
        result_message = "SUSPECT" if result == SheriffResult.SUSPICIOUS else "NON SUSPECT"
        
        return True, f"Investigation terminée : {target_name} est {result_message}"
    
    def perform_investigator_investigation(self, game_id, investigator_name, target_name):
        """Effectue une investigation Investigator"""
        if game_id not in self.games:
            return False, "Game not found"
        
        game = self.games[game_id]
        
        if investigator_name not in game['players']:
            return False, "Investigator not found"
        
        investigator = game['players'][investigator_name]
        
        # Vérifications de base
        if investigator['role'] != Role.INVESTIGATOR:
            return False, "Seul l'Investigator peut faire des investigations détaillées"
        
        if not investigator['alive']:
            return False, "Les morts ne peuvent pas investiguer"
        
        if game['phase'] != Phase.NIGHT:
            return False, "Les investigations se font la nuit"
        
        if target_name not in game['players']:
            return False, "Cible non trouvée"
        
        target = game['players'][target_name]
        
        if not target['alive']:
            return False, "Impossible d'investiguer un mort"
        
        if target_name == investigator_name:
            return False, "Vous ne pouvez pas vous investiguer vous-même"
        
        # Effectuer l'investigation
        group = self._get_investigator_group(target['role'])
        message = self._get_investigation_group_message(group)
        
        # Stocker le résultat
        if investigator_name not in game['investigation_results']:
            game['investigation_results'][investigator_name] = []
        
        investigation_data = {
            'investigator': investigator_name,
            'target': target_name,
            'result': group.value,
            'result_message': message,
            'result_type': 'investigator',
            'night': game.get('day_count', 1),
            'timestamp': datetime.now().isoformat()
        }
        
        game['investigation_results'][investigator_name].append(investigation_data)
        game['investigation_history'].append(investigation_data)
        
        return True, f"Investigation terminée : {message}"
    
    def get_investigation_results(self, game_id, player_name):
        """Récupère les résultats d'investigation d'un joueur"""
        if game_id not in self.games:
            return []
        
        game = self.games[game_id]
        
        return game['investigation_results'].get(player_name, [])
    
    def get_investigation_history(self, game_id):
        """Récupère l'historique complet des investigations"""
        if game_id not in self.games:
            return []
        
        return game['investigation_history']

# Global game engine instance
game_engine = GameEngine() 