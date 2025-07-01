from enum import Enum
import random
from datetime import datetime, timedelta

class Role(Enum):
    # TOWN ROLES (Village)
    VILLAGER = "villager"
    SEER = "seer"
    WITCH = "witch"
    GUARD = "bodyguard"           # Legacy - protection basique
    HUNTER = "hunter"
    SHERIFF = "sheriff"           # Détecte "Suspect" vs "Not Suspicious"  
    INVESTIGATOR = "investigator" # Donne indices sur type de rôle
    
    # 🆕 PHASE 3 - RÔLES DÉFENSIFS TOWN
    BODYGUARD = "bodyguard_new"   # Protection sacrificielle d'autres joueurs
    VETERAN = "veteran"           # Auto-défense + contre-attaque mortelle
    DOCTOR = "doctor"             # Soins préventifs et guérison
    
    # 🆕 PHASE 4 - RÔLES NEUTRES
    SURVIVOR = "survivor"         # Doit survivre jusqu'à la fin
    SERIAL_KILLER = "serial_killer"  # Tueur indépendant
    JESTER = "jester"            # Veut être lynché pour gagner
    
    # 🆕 PHASE 5 - RÔLES INVESTIGATIFS AVANCÉS
    LOOKOUT = "lookout"          # Observe qui visite sa cible
    SPY = "spy"                  # Écoute chat Mafia + voit visites
    DETECTIVE = "detective"      # Investigation avec historique
    
    # MAFIA ROLES (Faction Mafia)
    WEREWOLF = "werewolf"         # Legacy - sera remplacé par Mafioso
    GODFATHER = "godfather"       # Leader mafia, immunité investigation
    MAFIOSO = "mafioso"           # Tueur principal mafia
    BLACKMAILER = "blackmailer"   # Empêche de parler le jour
    CONSIGLIERE = "consigliere"   # Investigation pour la mafia

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
    MAFIA = "mafia"                # Godfather, Mafioso, Consigliere

# 🆕 PHASE 1 - ENUMS SYSTÈME MAFIA
class Faction(Enum):
    TOWN = "town"                  # Village/Innocent
    MAFIA = "mafia"               # Faction Mafia
    NEUTRAL = "neutral"           # Rôles neutres (Survivor, Serial Killer, Jester)

class DefenseLevel(Enum):
    NONE = "none"                 # Pas de défense
    BASIC = "basic"               # Défense basique
    POWERFUL = "powerful"         # Défense puissante

class AttackLevel(Enum):
    NONE = "none"                 # Pas d'attaque
    BASIC = "basic"               # Attaque basique
    POWERFUL = "powerful"         # Attaque puissante
    UNSTOPPABLE = "unstoppable"   # Traverse toute défense

class SpecialStatus(Enum):
    BLACKMAILED = "blackmailed"   # Ne peut pas parler
    ROLEBLOCKED = "roleblocked"   # Action bloquée
    FRAMED = "framed"             # Apparait suspect
    DISGUISED = "disguised"       # Apparait comme un autre rôle

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
            
            # 🆕 PHASE 1 - SYSTÈME MAFIA
            'mafia_members': [],                  # Liste des membres mafia
            'blackmailed_players': [],            # Joueurs blackmailés (ne peuvent pas parler)
            'special_statuses': {},               # Statuts spéciaux par joueur
            'investigation_immunities': {},       # Immunités d'investigation
            'defense_levels': {},                 # Niveaux de défense par joueur
            'attack_levels': {},                  # Niveaux d'attaque par joueur
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
        """🆕 PHASE 1 - Distribution avec Faction Mafia"""
        player_count = len(game['players'])
        player_names = list(game['players'].keys())
        random.shuffle(player_names)
        
        # 🆕 Nouvelle distribution équilibrée Town vs Mafia
        if player_count <= 6:
            mafia_count = 2  # Godfather + 1 autre
            town_special = 3  # seer + witch + sheriff/investigator
        elif player_count <= 10:
            mafia_count = 3  # Godfather + Mafioso + 1 autre
            town_special = 4  # seer + witch + guard + sheriff/investigator
        elif player_count <= 14:
            mafia_count = 4  # Tous les rôles mafia
            town_special = 7  # seer + witch + guard + hunter + sheriff + investigator + 1 avancé
        else:
            mafia_count = 4  # Tous les rôles mafia
            town_special = 9  # seer + witch + guard + hunter + sheriff + investigator + 2 avancés + défensif
        
        roles_to_assign = []
        
        # 🆕 DISTRIBUTION FACTION MAFIA
        mafia_roles_pool = [Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]
        
        # Godfather toujours présent
        roles_to_assign.append(Role.GODFATHER)
        mafia_roles_pool.remove(Role.GODFATHER)
        
        # Ajouter autres rôles mafia selon la taille
        for _ in range(mafia_count - 1):
            if mafia_roles_pool:
                role = random.choice(mafia_roles_pool)
                roles_to_assign.append(role)
                mafia_roles_pool.remove(role)
        
        # DISTRIBUTION TOWN (Village)
        # Core roles toujours présents
        roles_to_assign.append(Role.SEER)
        roles_to_assign.append(Role.WITCH)
        
        # Rôles investigatifs selon taille
        if town_special >= 3:
            investigation_role = random.choice([Role.SHERIFF, Role.INVESTIGATOR])
            roles_to_assign.append(investigation_role)
            
        if town_special >= 4:
            # 🆕 PHASE 3 - Nouveaux rôles défensifs prioritaires
            defensive_role = random.choice([Role.BODYGUARD, Role.DOCTOR, Role.GUARD])
            roles_to_assign.append(defensive_role)
            
        if town_special >= 5:
            # Ajouter Veteran ou Hunter
            combat_role = random.choice([Role.VETERAN, Role.HUNTER])
            roles_to_assign.append(combat_role)
            
        if town_special >= 6:
            # Ajouter l'autre rôle investigatif
            if Role.SHERIFF not in roles_to_assign:
                roles_to_assign.append(Role.SHERIFF)
            elif Role.INVESTIGATOR not in roles_to_assign:
                roles_to_assign.append(Role.INVESTIGATOR)
                
        if town_special >= 7:
            # Ajouter un autre rôle défensif
            remaining_defensive = [r for r in [Role.BODYGUARD, Role.DOCTOR, Role.GUARD] if r not in roles_to_assign]
            if remaining_defensive:
                roles_to_assign.append(random.choice(remaining_defensive))
                
        # 🆕 PHASE 5 - Rôles investigatifs avancés selon taille
        if town_special >= 8:
            # Ajouter un rôle investigatif avancé pour grandes parties
            available_advanced = [Role.LOOKOUT, Role.SPY, Role.DETECTIVE]
            advanced_role = random.choice(available_advanced)
            roles_to_assign.append(advanced_role)
            
        if town_special >= 9:
            # Ajouter un second rôle investigatif avancé pour très grandes parties
            remaining_advanced = [r for r in [Role.LOOKOUT, Role.SPY, Role.DETECTIVE] if r not in roles_to_assign]
            if remaining_advanced:
                roles_to_assign.append(random.choice(remaining_advanced))
        
        # 🆕 PHASE 4 - Rôles neutres selon taille (remplacent certains Town)
        neutral_count = 0
        if player_count >= 8:
            neutral_count = 1  # 1 neutre pour 8+ joueurs
        if player_count >= 12:
            neutral_count = 2  # 2 neutres pour 12+ joueurs
            
        # Ajouter les rôles neutres
        available_neutrals = [Role.SURVIVOR, Role.SERIAL_KILLER, Role.JESTER]
        for _ in range(neutral_count):
            if available_neutrals and len(roles_to_assign) < player_count:
                neutral_role = random.choice(available_neutrals)
                available_neutrals.remove(neutral_role)
                roles_to_assign.append(neutral_role)
        
        # Compléter avec des villageois
        while len(roles_to_assign) < player_count:
            roles_to_assign.append(Role.VILLAGER)
        
        # 🆕 Assigner rôles et configurer factions
        mafia_members = []
        for i, player_name in enumerate(player_names):
            role = roles_to_assign[i]
            game['players'][player_name]['role'] = role
            
            # 🆕 Configuration faction et capacités spéciales
            if role in [Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE, Role.WEREWOLF]:
                mafia_members.append(player_name)
                game['players'][player_name]['faction'] = Faction.MAFIA
                
                # Immunités spéciales
                if role == Role.GODFATHER:
                    game['investigation_immunities'][player_name] = True  # Immunité Sheriff
                    game['defense_levels'][player_name] = DefenseLevel.BASIC
                    
            elif role in [Role.SURVIVOR, Role.SERIAL_KILLER, Role.JESTER]:
                # 🆕 PHASE 4 - Configuration rôles neutres
                game['players'][player_name]['faction'] = Faction.NEUTRAL
                
                if role == Role.SURVIVOR:
                    game['defense_levels'][player_name] = DefenseLevel.BASIC  # Défense basique
                    game['players'][player_name]['survivor_vests'] = 4  # 4 gilets de protection
                elif role == Role.SERIAL_KILLER:
                    game['defense_levels'][player_name] = DefenseLevel.BASIC  # Défense basique
                    game['players'][player_name]['sk_cautious'] = False  # Mode prudent
                elif role == Role.JESTER:
                    # Jester n'a pas de capacités spéciales, juste condition victoire
                    pass
                    
            else:
                game['players'][player_name]['faction'] = Faction.TOWN
                
                # 🆕 PHASE 3 - Configuration défenses rôles Town
                if role == Role.VETERAN:
                    game['defense_levels'][player_name] = DefenseLevel.BASIC
                    game['players'][player_name]['veteran_alerts'] = 3  # 3 alertes max
                    game['players'][player_name]['veteran_on_alert'] = False
                elif role == Role.BODYGUARD:
                    game['players'][player_name]['bodyguard_vests'] = 1  # 1 gilet pare-balles
                elif role == Role.DOCTOR:
                    game['players'][player_name]['doctor_heals'] = 999  # Soins illimités
                
                # 🆕 PHASE 5 - Configuration rôles investigatifs avancés
                elif role == Role.LOOKOUT:
                    game['players'][player_name]['lookout_watches'] = 999  # Observations illimitées
                    game['players'][player_name]['lookout_results'] = []  # Historique observations
                elif role == Role.SPY:
                    game['players'][player_name]['spy_results'] = []  # Historique espionnage
                    game['players'][player_name]['mafia_visits'] = []  # Visites Mafia observées
                elif role == Role.DETECTIVE:
                    game['players'][player_name]['detective_results'] = []  # Historique investigations
                    game['players'][player_name]['detective_deductions'] = []  # Déductions
            
            print(f"DEBUG: Assigned {role.value} to {player_name}")
        
        # Sauvegarder les membres mafia
        game['mafia_members'] = mafia_members
        
        print(f"🆕 PHASE 1: Distribution finale - Mafia: {[r.value for r in roles_to_assign if r.value in ['godfather', 'mafioso', 'blackmailer', 'consigliere', 'werewolf']]}")
        print(f"🆕 PHASE 1: Membres mafia: {mafia_members}")
    
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
        
        # 🆕 Add mafia team info for all mafia roles
        if player['role'] in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]:
            mafia_team = [name for name, p in game['players'].items() 
                         if p['role'] in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE] and p['alive']]
            role_info['mafia_team'] = mafia_team
            role_info['faction'] = 'mafia'
        else:
            role_info['faction'] = 'town'
        
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
        
        # 🆕 PHASE 1 - ACTIONS MAFIA
        elif player['role'] == Role.GODFATHER and action == 'kill':
            # Le Godfather peut ordonner un kill
            game['night_actions'][player_name]['mafia_kill'] = target
            return True, f"Vous ordonnez l'élimination de {target}. Votre Mafioso exécutera l'ordre."
            
        elif player['role'] == Role.MAFIOSO and action == 'kill':
            # Le Mafioso exécute les kills
            game['night_actions'][player_name]['mafia_kill'] = target
            return True, f"Vous vous préparez à éliminer {target} cette nuit."
            
        elif player['role'] == Role.BLACKMAILER and action == 'blackmail':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            game['night_actions'][player_name]['blackmail'] = target
            player['night_action_used'] = True
            return True, f"Vous faites chanter {target}. Cette personne ne pourra pas parler demain."
            
        elif player['role'] == Role.CONSIGLIERE and action == 'investigate':
            # Investigation mafia - révèle le rôle exact
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            if target and target in game['players'] and game['players'][target]['alive']:
                success, message = self.perform_consigliere_investigation(game_id, player_name, target)
                if success:
                    player['night_action_used'] = True
                return success, message
            else:
                return False, "Cible invalide pour l'investigation"
        
        # 🆕 PHASE 3 - ACTIONS DÉFENSIVES TOWN
        elif player['role'] == Role.BODYGUARD and action == 'protect':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            # Vérifier si des gilets restants
            if player.get('bodyguard_vests', 0) <= 0:
                return False, "Plus de gilets pare-balles disponibles"
                
            if target and target in game['players'] and game['players'][target]['alive'] and target != player_name:
                game['night_actions'][player_name]['bodyguard_protect'] = target
                player['night_action_used'] = True
                return True, f"Vous protégez {target} cette nuit. Vous mourrez à sa place si il/elle est attaqué(e)."
            else:
                return False, "Cible invalide pour la protection (vous ne pouvez pas vous protéger)"
                
        elif player['role'] == Role.VETERAN and action == 'alert':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            # Vérifier si des alertes restantes
            if player.get('veteran_alerts', 0) <= 0:
                return False, "Plus d'alertes disponibles"
                
            # Vérifier si déjà en alerte
            if player.get('veteran_on_alert', False):
                return False, "Vous êtes déjà en alerte"
                
            game['night_actions'][player_name]['veteran_alert'] = True
            player['night_action_used'] = True
            player['veteran_on_alert'] = True
            return True, "Vous êtes maintenant en alerte ! Vous tuerez tous ceux qui vous visitent cette nuit."
            
        elif player['role'] == Role.DOCTOR and action == 'heal':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            if target and target in game['players'] and game['players'][target]['alive'] and target != player_name:
                game['night_actions'][player_name]['doctor_heal'] = target
                player['night_action_used'] = True
                return True, f"Vous soignez {target} cette nuit. Il/elle sera protégé(e) des attaques."
            else:
                return False, "Cible invalide pour les soins (vous ne pouvez pas vous soigner)"
        
        # 🆕 PHASE 4 - ACTIONS NEUTRES
        elif player['role'] == Role.SURVIVOR and action == 'vest':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            # Vérifier si des gilets restants
            if player.get('survivor_vests', 0) <= 0:
                return False, "Plus de gilets de protection disponibles"
                
            game['night_actions'][player_name]['survivor_vest'] = True
            player['night_action_used'] = True
            return True, "Vous enfilez un gilet de protection. Vous serez protégé des attaques cette nuit."
            
        elif player['role'] == Role.SERIAL_KILLER and action == 'kill':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            if target and target in game['players'] and game['players'][target]['alive'] and target != player_name:
                game['night_actions'][player_name]['sk_kill'] = target
                player['night_action_used'] = True
                return True, f"Vous vous préparez à éliminer {target} cette nuit. Personne ne vous arrêtera."
            else:
                return False, "Cible invalide pour l'élimination"
                
        elif player['role'] == Role.SERIAL_KILLER and action == 'cautious':
            # Mode prudent : pas d'action, mais défense renforcée
            if player.get('night_action_used', False):
                return False, "Vous avez déjà choisi votre action cette nuit"
                
            game['night_actions'][player_name]['sk_cautious'] = True
            player['night_action_used'] = True
            player['sk_cautious'] = True
            return True, "Vous restez prudent cette nuit. Votre défense est renforcée mais vous n'attaquez pas."
        
        # 🆕 PHASE 5 - ACTIONS INVESTIGATIVES AVANCÉES
        elif player['role'] == Role.LOOKOUT and action == 'watch':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            if target and target in game['players'] and game['players'][target]['alive'] and target != player_name:
                game['night_actions'][player_name]['lookout_watch'] = target
                player['night_action_used'] = True
                return True, f"Vous surveillez {target} cette nuit. Vous verrez qui lui rend visite."
            else:
                return False, "Cible invalide pour la surveillance (vous ne pouvez pas vous surveiller)"
                
        elif player['role'] == Role.SPY and action == 'spy':
            # Spy observe automatiquement sans cible
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            game['night_actions'][player_name]['spy_watch'] = True
            player['night_action_used'] = True
            return True, "Vous espionnez cette nuit. Vous verrez toutes les visites Mafia et entendrez leur chat."
            
        elif player['role'] == Role.DETECTIVE and action == 'investigate':
            # Vérifier si déjà utilisé cette nuit
            if player.get('night_action_used', False):
                return False, "Vous avez déjà utilisé votre pouvoir cette nuit"
                
            if target and target in game['players'] and game['players'][target]['alive'] and target != player_name:
                success, message = self.perform_detective_investigation(game_id, player_name, target)
                if success:
                    player['night_action_used'] = True
                return success, message
            else:
                return False, "Cible invalide pour l'investigation détective"
        
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
                
                # 🆕 PHASE 2 - Nettoyer la liste des joueurs blackmailés (effet terminé)
                game['blackmailed_players'] = []
                
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
        """🆕 PHASE 3 - Process all night actions (avec rôles défensifs)"""
        # 🆕 PHASE 3 - Traitement des protections avancées
        protected_players = set()
        bodyguard_protections = {}  # target -> bodyguard_name
        doctor_heals = set()
        veteran_alerts = set()
        
        # First, apply all protections
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            
            # Legacy Guard protection
            if 'protect' in actions:
                target = actions['protect']
                if target in game['players']:
                    game['players'][target]['protected'] = True
                    protected_players.add(target)
            
            # 🆕 Bodyguard protection (sacrificielle)
            elif 'bodyguard_protect' in actions:
                target = actions['bodyguard_protect']
                if target in game['players']:
                    bodyguard_protections[target] = player_name
                    protected_players.add(target)
                    # Consommer un gilet
                    player['bodyguard_vests'] = max(0, player.get('bodyguard_vests', 1) - 1)
            
            # 🆕 Doctor heal
            elif 'doctor_heal' in actions:
                target = actions['doctor_heal']
                if target in game['players']:
                    doctor_heals.add(target)
                    protected_players.add(target)
            
            # 🆕 Veteran alert
            elif 'veteran_alert' in actions:
                veteran_alerts.add(player_name)
                # Consommer une alerte
                player['veteran_alerts'] = max(0, player.get('veteran_alerts', 3) - 1)
                player['veteran_on_alert'] = True
        
        # 🆕 PHASE 4 - Traitement des actions neutres
        survivor_vests = set()
        sk_targets = {}  # sk_name -> target
        sk_cautious = set()
        
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            
            # Survivor vest
            if 'survivor_vest' in actions:
                survivor_vests.add(player_name)
                # Consommer un gilet
                player['survivor_vests'] = max(0, player.get('survivor_vests', 4) - 1)
                # Ajouter défense temporaire
                game['defense_levels'][player_name] = DefenseLevel.BASIC
                
            # Serial Killer kill
            elif 'sk_kill' in actions:
                target = actions['sk_kill']
                if target in game['players']:
                    sk_targets[player_name] = target
                    
            # Serial Killer cautious
            elif 'sk_cautious' in actions:
                sk_cautious.add(player_name)
                # Défense renforcée en mode prudent
                game['defense_levels'][player_name] = DefenseLevel.BASIC
        
        # 🆕 PHASE 5 - Traitement des actions investigatives avancées
        lookout_watches = {}  # lookout_name -> target_watched
        spy_results = []      # Résultats espionnage
        
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            
            # Lookout watch
            if 'lookout_watch' in actions:
                target = actions['lookout_watch']
                if target in game['players']:
                    lookout_watches[player_name] = target
                    
            # Spy watch (automatique)
            elif 'spy_watch' in actions:
                spy_results.append(player_name)
        
        # 🆕 PHASE 1 - Coordination des kills Mafia
        mafia_target = None
        mafia_killer = None
        
        # Priorité au Godfather s'il ordonne un kill
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            if player['role'] == Role.GODFATHER and 'mafia_kill' in actions:
                mafia_target = actions['mafia_kill']
                mafia_killer = player_name
                break
        
        # Si pas de Godfather, chercher un Mafioso ou Werewolf
        if not mafia_target:
            for player_name, actions in game['night_actions'].items():
                player = game['players'][player_name]
                if ((player['role'] == Role.MAFIOSO and 'mafia_kill' in actions) or
                    (player['role'] == Role.WEREWOLF and 'kill' in actions)):
                    mafia_target = actions.get('mafia_kill') or actions.get('kill')
                    mafia_killer = player_name
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
        
        # 🆕 PHASE 1 - Traitement du Blackmail
        blackmail_target = None
        for player_name, actions in game['night_actions'].items():
            player = game['players'][player_name]
            if player['role'] == Role.BLACKMAILER and 'blackmail' in actions:
                blackmail_target = actions['blackmail']
                # Ajouter à la liste des blackmailés pour le jour suivant
                if blackmail_target not in game['blackmailed_players']:
                    game['blackmailed_players'].append(blackmail_target)
                break
        
        # Collect elimination stories for combined message
        elimination_stories = []
        
        # 🆕 PHASE 3 - Resolve Mafia kills (avec système de défense avancé)
        if mafia_target and mafia_target in game['players']:
            target_player = game['players'][mafia_target]
            
            # 🆕 Vérifier si le Veteran est en alerte et tue l'attaquant
            if mafia_target in veteran_alerts:
                # Veteran tue l'attaquant !
                if mafia_killer and mafia_killer in game['players']:
                    killer_player = game['players'][mafia_killer]
                    killer_player['alive'] = False
                    
                    eliminated_info = {
                        'name': mafia_killer,
                        'cause': 'veteran_kill',
                        'day': game['day_count'],
                        'role': killer_player['role'].value if isinstance(killer_player['role'], Role) else killer_player['role']
                    }
                    game['eliminated_players'].append(eliminated_info)
                    elimination_stories.append(f"⚔️ {mafia_killer} a tenté d'attaquer {mafia_target}, mais le Veteran était en alerte ! L'attaquant a été éliminé.")
                    
                    # Révéler testament
                    self.reveal_will_on_death(game, mafia_killer)
                
                # Veteran survit grâce à sa défense
                game['game_history'].append({
                    'type': 'veteran_defense',
                    'phase': 'night',
                    'day': game['day_count'],
                    'player': mafia_target,
                    'killer': mafia_killer,
                    'description': f"{mafia_target} (Veteran) a tué {mafia_killer} qui tentait de l'attaquer"
                })
                
            else:
                # 🆕 PHASE 3 - Système de défense avancé avec priorités
                
                # 1. Vérifier Doctor/Witch heal en priorité (évite sacrifice Bodyguard)
                if mafia_target in doctor_heals or mafia_target == witch_heal_target:
                    protection_type = "soins du Doctor" if mafia_target in doctor_heals else "potion de guérison"
                    game['game_history'].append({
                        'type': 'defense',
                        'phase': 'night',
                        'day': game['day_count'],
                        'player': mafia_target,
                        'description': f"{mafia_target} a survécu à une attaque grâce à sa {protection_type}"
                    })
                    
                # 2. Vérifier protection Bodyguard (sacrificielle)
                elif mafia_target in bodyguard_protections:
                    bodyguard_name = bodyguard_protections[mafia_target]
                    bodyguard_player = game['players'][bodyguard_name]
                    
                    # Bodyguard meurt à la place
                    bodyguard_player['alive'] = False
                    eliminated_info = {
                        'name': bodyguard_name,
                        'cause': 'bodyguard_sacrifice',
                        'day': game['day_count'],
                        'role': bodyguard_player['role'].value if isinstance(bodyguard_player['role'], Role) else bodyguard_player['role']
                    }
                    game['eliminated_players'].append(eliminated_info)
                    elimination_stories.append(f"🛡️ {bodyguard_name} s'est sacrifié pour protéger {mafia_target}. Le Bodyguard a pris la balle à sa place.")
                    
                    # Révéler testament du bodyguard
                    self.reveal_will_on_death(game, bodyguard_name)
                    
                    # Cible survit
                    game['game_history'].append({
                        'type': 'bodyguard_sacrifice',
                        'phase': 'night',
                        'day': game['day_count'],
                        'bodyguard': bodyguard_name,
                        'protected': mafia_target,
                        'description': f"{bodyguard_name} s'est sacrifié pour sauver {mafia_target}"
                    })
                    
                else:
                    # 3. Vérifier autres protections (Guard, défense naturelle)
                    is_protected = game['players'][mafia_target].get('protected', False)
                    target_defense = game['defense_levels'].get(mafia_target, DefenseLevel.NONE)
                    
                    # Mafia kill = Basic attack par défaut
                    attack_level = AttackLevel.BASIC
                    
                    # Résoudre attaque vs défense
                    kill_succeeds = not is_protected and target_defense == DefenseLevel.NONE
                    
                    if kill_succeeds:
                        # Kill normal
                        target_player['alive'] = False
                        eliminated_info = {
                            'name': mafia_target,
                            'cause': 'mafia_kill',
                            'day': game['day_count'],
                            'role': target_player['role'].value if isinstance(target_player['role'], Role) else target_player['role']
                        }
                        game['eliminated_players'].append(eliminated_info)
                        elimination_stories.append(self._generate_death_story(mafia_target, 'mafia_kill', target_player['role']))
                        
                        # 🆕 Révéler testament et note de mort
                        self.reveal_will_on_death(game, mafia_target)
                        
                        if mafia_killer:
                            self.reveal_death_note_on_kill(game, mafia_killer, mafia_target)
                        
                        # Ajouter à l'historique
                        game['game_history'].append({
                            'type': 'elimination',
                            'phase': 'night',
                            'day': game['day_count'],
                            'player': mafia_target,
                            'cause': 'mafia_kill',
                            'role': eliminated_info['role'],
                            'description': f"{mafia_target} ({eliminated_info['role']}) a été éliminé par la Mafia"
                        })
                        
                    else:
                        # Message de défense réussie
                        protection_type = "défense naturelle"
                        if game['players'][mafia_target].get('protected', False):
                            protection_type = "protection du Garde"
                        elif target_defense != DefenseLevel.NONE:
                            protection_type = "défense naturelle"
                           
                        game['game_history'].append({
                            'type': 'defense',
                            'phase': 'night',
                            'day': game['day_count'],
                            'player': mafia_target,
                            'description': f"{mafia_target} a survécu à une attaque grâce à sa {protection_type}"
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
        
        # 🆕 PHASE 4 - Traitement des kills Serial Killer
        for sk_name, sk_target in sk_targets.items():
            if sk_target in game['players'] and game['players'][sk_target]['alive']:
                target_player = game['players'][sk_target]
                
                # Vérifier si le Veteran est en alerte et tue le SK
                if sk_target in veteran_alerts:
                    # Veteran tue le Serial Killer !
                    sk_player = game['players'][sk_name]
                    sk_player['alive'] = False
                    
                    eliminated_info = {
                        'name': sk_name,
                        'cause': 'veteran_kill',
                        'day': game['day_count'],
                        'role': sk_player['role'].value if isinstance(sk_player['role'], Role) else sk_player['role']
                    }
                    game['eliminated_players'].append(eliminated_info)
                    elimination_stories.append(f"⚔️ {sk_name} a tenté d'attaquer {sk_target}, mais le Veteran était en alerte ! Le Serial Killer a été éliminé.")
                    
                    # Révéler testament
                    self.reveal_will_on_death(game, sk_name)
                    
                else:
                    # Système de défense normal pour SK kill
                    is_protected = (sk_target in doctor_heals or 
                                  sk_target == witch_heal_target or
                                  sk_target in bodyguard_protections or
                                  game['players'][sk_target].get('protected', False))
                    target_defense = game['defense_levels'].get(sk_target, DefenseLevel.NONE)
                    
                    # Serial Killer kill = Basic attack
                    kill_succeeds = not is_protected and target_defense == DefenseLevel.NONE
                    
                    if kill_succeeds:
                        # SK kill réussi
                        target_player['alive'] = False
                        eliminated_info = {
                            'name': sk_target,
                            'cause': 'serial_killer',
                            'day': game['day_count'],
                            'role': target_player['role'].value if isinstance(target_player['role'], Role) else target_player['role']
                        }
                        game['eliminated_players'].append(eliminated_info)
                        elimination_stories.append(f"🔪 {sk_target} a été retrouvé mort, victime d'un tueur en série. Les méthodes brutales ne laissent aucun doute...")
                        
                        # Révéler testament
                        self.reveal_will_on_death(game, sk_target)
                        
                        # Ajouter à l'historique
                        game['game_history'].append({
                            'type': 'elimination',
                            'phase': 'night',
                            'day': game['day_count'],
                            'player': sk_target,
                            'cause': 'serial_killer',
                            'role': eliminated_info['role'],
                            'description': f"{sk_target} ({eliminated_info['role']}) a été éliminé par le Serial Killer"
                        })
        
        # 🆕 PHASE 3 - Reset des états temporaires
        for player_name, player in game['players'].items():
            # Reset veteran alert status
            if player.get('veteran_on_alert', False):
                player['veteran_on_alert'] = False
            # Reset survivor vest defense
            if player_name in survivor_vests:
                if player.get('survivor_vests', 0) == 0:
                    # Plus de gilets, retirer la défense permanente
                    if game['defense_levels'].get(player_name) == DefenseLevel.BASIC:
                        game['defense_levels'][player_name] = DefenseLevel.NONE
            # Reset SK cautious defense
            if player_name in sk_cautious:
                player['sk_cautious'] = False
                # Retirer défense temporaire
                if game['defense_levels'].get(player_name) == DefenseLevel.BASIC:
                    game['defense_levels'][player_name] = DefenseLevel.NONE
        
        # 🆕 PHASE 5 - Traitement des résultats investigatifs avancés
        
        # Traiter les observations Lookout
        for lookout_name, watched_target in lookout_watches.items():
            lookout_player = game['players'][lookout_name]
            visitors = []
            
            # Chercher qui a visité la cible
            for visitor_name, actions in game['night_actions'].items():
                if visitor_name == lookout_name:
                    continue  # Le Lookout ne se voit pas
                    
                # Vérifier toutes les actions qui ciblent watched_target
                for action_type, target in actions.items():
                    if target == watched_target:
                        visitors.append(visitor_name)
                        break
            
            # Créer le résultat d'observation
            if visitors:
                visitor_list = ", ".join(visitors)
                observation_message = f"🔍 OBSERVATION: {visitor_list} a/ont visité {watched_target} cette nuit."
            else:
                observation_message = f"🔍 OBSERVATION: Personne n'a visité {watched_target} cette nuit."
            
            # Sauvegarder le résultat
            if 'lookout_results' not in lookout_player:
                lookout_player['lookout_results'] = []
            
            lookout_result = {
                'watched': watched_target,
                'visitors': visitors,
                'message': observation_message,
                'night': game['day_count'],
                'timestamp': datetime.now().isoformat()
            }
            
            lookout_player['lookout_results'].append(lookout_result)
            
            # Ajouter aux résultats d'investigation
            if lookout_name not in game['investigation_results']:
                game['investigation_results'][lookout_name] = []
            
            game['investigation_results'][lookout_name].append({
                'investigator': lookout_name,
                'target': watched_target,
                'result': visitor_list if visitors else "Aucun visiteur",
                'result_message': observation_message,
                'result_type': 'lookout',
                'night': game['day_count'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Traiter les résultats Spy
        for spy_name in spy_results:
            spy_player = game['players'][spy_name]
            
            # Observer les visites Mafia
            mafia_visits = []
            if mafia_target and mafia_killer:
                mafia_visits.append(f"{mafia_killer} a visité {mafia_target}")
            
            # Observer les actions Mafia (blackmail, etc.)
            for player_name, actions in game['night_actions'].items():
                player = game['players'][player_name]
                if player['role'] in [Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]:
                    for action_type, target in actions.items():
                        if action_type == 'blackmail':
                            mafia_visits.append(f"{player_name} a fait chanter {target}")
                        elif action_type == 'consigliere' and target:
                            mafia_visits.append(f"{player_name} a enquêté sur {target}")
            
            # Créer le message d'espionnage
            if mafia_visits:
                spy_message = f"🕵️ ESPIONNAGE: " + " | ".join(mafia_visits)
            else:
                spy_message = f"🕵️ ESPIONNAGE: Aucune activité Mafia détectée cette nuit."
            
            # Sauvegarder le résultat
            if 'spy_results' not in spy_player:
                spy_player['spy_results'] = []
            
            spy_result = {
                'mafia_visits': mafia_visits,
                'message': spy_message,
                'night': game['day_count'],
                'timestamp': datetime.now().isoformat()
            }
            
            spy_player['spy_results'].append(spy_result)
            
            # Ajouter aux résultats d'investigation
            if spy_name not in game['investigation_results']:
                game['investigation_results'][spy_name] = []
            
            game['investigation_results'][spy_name].append({
                'investigator': spy_name,
                'target': 'Mafia',
                'result': str(len(mafia_visits)) + " activités",
                'result_message': spy_message,
                'result_type': 'spy',
                'night': game['day_count'],
                'timestamp': datetime.now().isoformat()
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
        """🆕 PHASE 4 - Vérification de fin de jeu avec rôles neutres"""
        alive_players = [p for p in game['players'].values() if p['alive']]
        
        if len(alive_players) == 0:
            # Tout le monde est mort - match nul
            game['winner'] = 'draw'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            return True
        
        # Compter par factions
        alive_mafia = [p for p in alive_players if p['role'] in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]]
        alive_town = [p for p in alive_players if p['role'] not in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE, Role.SURVIVOR, Role.SERIAL_KILLER, Role.JESTER]]
        alive_neutrals = [p for p in alive_players if p['role'] in [Role.SURVIVOR, Role.SERIAL_KILLER, Role.JESTER]]
        
        # 🆕 PHASE 4 - Vérifier victoires neutres spéciales
        
        # Victoire Serial Killer : Seul survivant ou égalité avec 1 autre
        alive_sk = [p for p in alive_players if p['role'] == Role.SERIAL_KILLER]
        if alive_sk and len(alive_players) <= 2 and len(alive_mafia) == 0 and len(alive_town) == 0:
            game['winner'] = 'serial_killer'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            game['game_history'].append({
                'type': 'game_end',
                'phase': 'end',
                'day': game['day_count'],
                'winner': 'serial_killer',
                'description': '🔪 Victoire du Serial Killer ! Il a éliminé tous ses ennemis.'
            })
            return True
        
        # Victoire Jester : Déjà gérée dans _execute_accused si lynché
        
        # Victoire Town : Plus de Mafia vivants (neutres survivent avec Town)
        if len(alive_mafia) == 0 and len(alive_sk) == 0:
            game['winner'] = 'town'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            
            # Vérifier si des Survivors gagnent aussi
            survivors = [p for p in alive_players if p['role'] == Role.SURVIVOR]
            winner_desc = '🎉 Victoire du Village ! Toute la Mafia a été éliminée.'
            if survivors:
                survivor_names = [name for name, p in game['players'].items() if p in survivors]
                winner_desc += f' Les Survivors {", ".join(survivor_names)} survivent également !'
            
            game['game_history'].append({
                'type': 'game_end',
                'phase': 'end',
                'day': game['day_count'],
                'winner': 'town',
                'description': winner_desc
            })
            return True
        
        # Victoire Mafia : Égalité ou majorité mafia (sans compter SK)
        non_mafia_non_sk = len(alive_town) + len([p for p in alive_neutrals if p['role'] != Role.SERIAL_KILLER])
        if len(alive_mafia) >= non_mafia_non_sk and len(alive_sk) == 0:
            game['winner'] = 'mafia'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            
            # Vérifier si des Survivors gagnent aussi
            survivors = [p for p in alive_players if p['role'] == Role.SURVIVOR]
            winner_desc = '🏴‍☠️ Victoire de la Mafia ! Ils contrôlent maintenant le village.'
            if survivors:
                survivor_names = [name for name, p in game['players'].items() if p in survivors]
                winner_desc += f' Les Survivors {", ".join(survivor_names)} survivent également !'
                
            game['game_history'].append({
                'type': 'game_end',
                'phase': 'end',
                'day': game['day_count'],
                'winner': 'mafia',
                'description': winner_desc
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
        if not self._can_send_message(game, player, channel, player_name):
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
    
    def _can_send_message(self, game, player, channel, player_name):
        """🆕 PHASE 2 - Vérifie si un joueur peut envoyer un message (avec système blackmail)"""
        player_role = player['role']
        player_alive = player['alive']
        current_phase = game['phase']
        
        if channel == ChatChannel.PUBLIC:
            # 🆕 Vérifier si le joueur est blackmailé
            if player_name and player_name in game.get('blackmailed_players', []):
                return False  # Les joueurs blackmailés ne peuvent pas parler
                
            # Chat public : seulement pendant le jour et si vivant
            return current_phase in [Phase.DAY, Phase.VOTING, Phase.TRIAL] and player_alive
            
        elif channel == ChatChannel.MAFIA:
            # 🆕 Chat mafia : étendu à tous les rôles Mafia
            mafia_roles = [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]
            return (current_phase == Phase.NIGHT and 
                   player_role in mafia_roles and 
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
            # Messages privés : toujours autorisés si vivant (même si blackmailé)
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
            
            # 🆕 PHASE 1 - ACTIONS MAFIA
            elif player['role'] == Role.GODFATHER and not player.get('night_action_used', False):
                # Godfather peut ordonner un kill sur n'importe qui d'autre
                non_mafia_targets = [name for name, p in game['players'].items() 
                                   if p['alive'] and name != player_name and 
                                   p['role'] not in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]]
                if non_mafia_targets:
                    actions.append({
                        'type': 'kill',
                        'description': 'Ordonner l\'élimination d\'un ennemi',
                        'targets': non_mafia_targets
                    })
            
            elif player['role'] == Role.MAFIOSO and not player.get('night_action_used', False):
                # Mafioso peut tuer si pas d'ordre du Godfather
                non_mafia_targets = [name for name, p in game['players'].items() 
                                   if p['alive'] and name != player_name and 
                                   p['role'] not in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]]
                if non_mafia_targets:
                    actions.append({
                        'type': 'kill',
                        'description': 'Éliminer un ennemi de la famille',
                        'targets': non_mafia_targets
                    })
            
            elif player['role'] == Role.BLACKMAILER and not player.get('night_action_used', False):
                # Blackmailer peut blackmail n'importe qui d'autre
                non_mafia_targets = [name for name, p in game['players'].items() 
                                   if p['alive'] and name != player_name and 
                                   p['role'] not in [Role.WEREWOLF, Role.GODFATHER, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE]]
                if non_mafia_targets:
                    actions.append({
                        'type': 'blackmail',
                        'description': 'Faire chanter un joueur (l\'empêche de parler demain)',
                        'targets': non_mafia_targets
                    })
            
            elif player['role'] == Role.CONSIGLIERE and not player.get('night_action_used', False):
                # Consigliere peut investiguer n'importe qui d'autre
                if alive_others:
                    actions.append({
                        'type': 'investigate',
                        'description': 'Investigation précise (révèle le rôle exact)',
                        'targets': alive_others
                    })
            
            # 🆕 PHASE 3 - ACTIONS DÉFENSIVES TOWN
            elif player['role'] == Role.BODYGUARD and not player.get('night_action_used', False):
                # Bodyguard peut protéger quelqu'un d'autre (pas lui-même)
                if alive_others and player.get('bodyguard_vests', 0) > 0:
                    actions.append({
                        'type': 'protect',
                        'description': f'Protéger un joueur (Gilets restants: {player.get("bodyguard_vests", 0)})',
                        'targets': alive_others
                    })
            
            elif player['role'] == Role.VETERAN and not player.get('night_action_used', False):
                # Veteran peut se mettre en alerte (auto-défense + contre-attaque)
                if player.get('veteran_alerts', 0) > 0 and not player.get('veteran_on_alert', False):
                    actions.append({
                        'type': 'alert',
                        'description': f'Se mettre en alerte (Alertes restantes: {player.get("veteran_alerts", 0)})',
                        'targets': []  # Pas de cible, action sur soi-même
                    })
            
            elif player['role'] == Role.DOCTOR and not player.get('night_action_used', False):
                # Doctor peut soigner quelqu'un d'autre (pas lui-même)
                if alive_others:
                    actions.append({
                        'type': 'heal',
                        'description': 'Soigner un joueur (prévient les attaques)',
                        'targets': alive_others
                    })
            
            # 🆕 PHASE 4 - ACTIONS NEUTRES
            elif player['role'] == Role.SURVIVOR and not player.get('night_action_used', False):
                # Survivor peut utiliser un gilet de protection
                if player.get('survivor_vests', 0) > 0:
                    actions.append({
                        'type': 'vest',
                        'description': f'Utiliser un gilet de protection (Gilets restants: {player.get("survivor_vests", 0)})',
                        'targets': []  # Pas de cible, action sur soi-même
                    })
            
            elif player['role'] == Role.SERIAL_KILLER and not player.get('night_action_used', False):
                # Serial Killer peut tuer ou rester prudent
                if alive_others:
                    actions.append({
                        'type': 'kill',
                        'description': 'Éliminer quelqu\'un cette nuit',
                        'targets': alive_others
                    })
                
                # Option mode prudent (défense renforcée)
                actions.append({
                    'type': 'cautious',
                    'description': 'Rester prudent (défense renforcée, pas d\'attaque)',
                    'targets': []  # Pas de cible
                })
            
            elif player['role'] == Role.JESTER:
                # Jester n'a pas d'actions nocturnes spéciales
                # Son objectif est de se faire lyncher le jour
                pass
            
            # 🆕 PHASE 5 - ACTIONS INVESTIGATIVES AVANCÉES
            elif player['role'] == Role.LOOKOUT and not player.get('night_action_used', False):
                # Lookout peut surveiller quelqu'un d'autre
                if alive_others:
                    actions.append({
                        'type': 'watch',
                        'description': 'Surveiller un joueur (voir qui lui rend visite)',
                        'targets': alive_others
                    })
            
            elif player['role'] == Role.SPY and not player.get('night_action_used', False):
                # Spy espionne automatiquement
                actions.append({
                    'type': 'spy',
                    'description': 'Espionner (voir visites Mafia + écouter leur chat)',
                    'targets': []  # Pas de cible nécessaire
                })
            
            elif player['role'] == Role.DETECTIVE and not player.get('night_action_used', False):
                # Detective peut investiguer avec historique
                if alive_others:
                    actions.append({
                        'type': 'investigate',
                        'description': 'Investigation détective (historique + déductions)',
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
                ],
                # 🆕 PHASE 1 - RÔLES MAFIA
                'godfather': [
                    f"🕴️ {player_name}, le Parrain respecté, a été abattu dans une embuscade sanglante. Un empire criminel s'effondre.",
                    f"💼 {player_name} repose dans un costume ensanglanté. Le chef de la famille a rendu son dernier souffle.",
                    f"👑 {player_name}, le roi du crime organisé, a été éliminé. Qui reprendra le contrôle de la famille ?"
                ],
                'mafioso': [
                    f"🔫 {player_name}, l'exécuteur de la famille, a été retrouvé criblé de balles. L'arme du crime a retourné contre lui.",
                    f"⚰️ {player_name} gît dans une flaque de sang, ses propres méthodes utilisées contre lui. La violence appelle la violence.",
                    f"💀 {player_name}, le bras armé de la mafia, a été éliminé par plus rusé que lui. L'élève a dépassé le maître."
                ],
                'blackmailer': [
                    f"🤐 {player_name}, qui connaissait tous les secrets, a été réduit au silence pour toujours. Ses dossiers brûlent avec lui.",
                    f"📋 {player_name} emporte ses chantages dans la tombe. Certains secrets meurent avec ceux qui les gardent.",
                    f"🗂️ {player_name}, maître des manipulations, a été manipulé à son tour. Les cartes se sont retournées contre lui."
                ],
                'consigliere': [
                    f"🎭 {player_name}, le conseiller de l'ombre, a été démasqué et éliminé. Ses stratégies n'ont pas pu le sauver.",
                    f"📚 {player_name} ferme ses dossiers pour la dernière fois. L'espion de la famille a été découvert.",
                    f"🕵️ {player_name}, qui savait tout sur tout le monde, n'a pas vu venir son propre destin. L'ironie du sort frappe fort."
                ]
            },
            'mafia_kill': {
                'villager': [
                    f"🕴️ {player_name} a été retrouvé(e) ce matin avec une balle dans la tête. La signature de la mafia est claire.",
                    f"💼 {player_name} repose dans une flaque de sang. Un règlement de comptes mafieux s'est déroulé cette nuit.",
                    f"🔫 {player_name} a été éliminé(e) par des professionnels. La famille a parlé, et elle ne se répète jamais."
                ],
                'seer': [
                    f"👁️ {player_name}, le/la voyant(e), a été assassiné(e) par la mafia. Ses visions se sont éteintes dans le sang.",
                    f"🔮 La mafia a fait taire {player_name} pour toujours. L'oracle du village ne parlera plus.",
                    f"🌟 {player_name} a vu sa propre mort arriver, mais n'a pas pu l'éviter. La prophétie s'est réalisée."
                ],
                'witch': [
                    f"🧪 {player_name}, la sorcière, a été exécutée par des tueurs professionnels. Ses potions n'ont pas pu la sauver.",
                    f"⚗️ La mafia a dévasté l'antre de {player_name}. Les fioles magiques se mélangent maintenant au sang.",
                    f"🍃 {player_name} gît parmi ses grimoires déchirés. La famille ne tolère pas la magie qui lui échappe."
                ],
                'bodyguard': [
                    f"🛡️ {player_name}, le/la garde, a été abattu(e) par des tireurs d'élite. Même les protecteurs ont besoin de protection.",
                    f"⚔️ La mafia a eu raison de {player_name} cette nuit. Le/la garde est tombé(e) sous les balles ennemies.",
                    f"🏰 {player_name} a livré son dernier combat contre des assassins impitoyables. L'honneur ne suffit pas contre les balles."
                ],
                'hunter': [
                    f"🏹 {player_name}, le/la chasseur/chasseuse, a été pris(e) au piège par la mafia. Les prédateurs sont devenus proies.",
                    f"🎯 La famille a tracké {player_name} toute la nuit. Le/la chasseur/chasseuse a été chassé(e) à son tour.",
                    f"🦌 {player_name} pensait traquer le gibier, mais c'est la mafia qui l'attendait. Le jeu s'est retourné contre lui/elle."
                ],
                # Mafia tuant mafia (guerre interne)
                'godfather': [
                    f"👑 {player_name}, le Parrain, a été renversé par sa propre famille. Une révolution sanglante a eu lieu.",
                    f"💼 {player_name} repose dans son bureau, trahi par ses propres hommes. Le pouvoir corrompt, même au sommet.",
                    f"🕴️ {player_name} a été éliminé(e) dans un coup d'État mafieux. L'empire change de mains cette nuit."
                ],
                'mafioso': [
                    f"🔫 {player_name} a été exécuté(e) par ordre de la famille. Désobéir au Parrain coûte cher.",
                    f"⚰️ {player_name} gît dans une ruelle sombre, victime de la justice mafieuse. La famille nettoie ses rangs.",
                    f"💀 {player_name} a connu le sort réservé aux traîtres. La mafia ne pardonne jamais."
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
                ],
                # 🆕 PHASE 1 - LYNCHAGES MAFIA
                'godfather': [
                    f"👑 {player_name}, le Parrain respecté, a été démasqué et pendu ({votes} votes). L'empire criminel s'effondre sous les yeux du village.",
                    f"🕴️ {player_name} garde sa dignité jusqu'à la fin, même face à la corde ({votes} votes). Un roi du crime tombe.",
                    f"💼 {player_name} emporte ses secrets dans la tombe. Le village a éliminé le chef de la famille ({votes} votes)."
                ],
                'mafioso': [
                    f"🔫 {player_name}, l'exécuteur de la famille, a été jugé et condamné ({votes} votes). Le tueur paie pour ses crimes.",
                    f"⚰️ {player_name} affronte son destin sans trembler ({votes} votes). Un homme de main de moins pour la mafia.",
                    f"💀 {player_name} reçoit la justice qu'il a refusée à ses victimes ({votes} votes). L'ironie du sort."
                ],
                'blackmailer': [
                    f"🤐 {player_name}, le maître-chanteur, a été réduit au silence pour toujours ({votes} votes). Ses secrets meurent avec lui.",
                    f"📋 {player_name} brûle avec ses dossiers compromettants ({votes} votes). Les chantages s'arrêtent ici.",
                    f"🗂️ {player_name} découvre qu'on ne peut pas faire chanter tout un village ({votes} votes). La justice collective triomphe."
                ],
                'consigliere': [
                    f"🎭 {player_name}, le conseiller de l'ombre, a été démasqué par ceux qu'il espionnait ({votes} votes). L'espion devient victime.",
                    f"📚 {player_name} ferme ses dossiers pour la dernière fois ({votes} votes). L'analyste n'a pas prévu sa propre fin.",
                    f"🕵️ {player_name}, qui savait tout sur tout le monde, n'a pas vu venir le village en colère ({votes} votes). L'ironie ultime."
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
        
        # 🆕 PHASE 4 - Vérifier victoire Jester AVANT élimination
        if accused_role == Role.JESTER:
            # Jester gagne immédiatement quand lynché !
            game['winner'] = 'jester'
            game['phase'] = Phase.ENDED
            game['status'] = 'ended'
            game['game_history'].append({
                'type': 'game_end',
                'phase': 'lynching',
                'day': game['day_count'],
                'winner': 'jester',
                'description': f'🎭 Victoire du Jester ! {accused} a réussi à se faire lyncher et gagne la partie !'
            })
            
            # Générer histoire spéciale pour Jester
            execution_story = f"🎭 {accused} éclate de rire alors que la corde se resserre. Le village réalise trop tard qu'ils viennent de lyncher un innocent Jester qui voulait mourir ! Il remporte la victoire dans un dernier éclat de rire macabre..."
            game['last_elimination'] = execution_story
            
            return True, f"🎭 {accused} (Jester) gagne en étant lynché !"
        
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
        if self._can_send_message(game, player, ChatChannel.PUBLIC, player_name):
            channels.append({
                'id': 'public',
                'name': 'Village',
                'description': 'Chat public du village',
                'color': '#3b82f6'
            })
        
        # Canal mafia
        if self._can_send_message(game, player, ChatChannel.MAFIA, player_name):
            channels.append({
                'id': 'mafia',
                'name': 'Famille',
                'description': 'Chat privé de la Mafia',
                'color': '#ef4444'
            })
        
        # Canal des morts
        if self._can_send_message(game, player, ChatChannel.DEAD, player_name):
            channels.append({
                'id': 'dead',
                'name': 'Outre-tombe',
                'description': 'Chat des esprits',
                'color': '#6b7280'
            })
        
        # Messages privés
        if self._can_send_message(game, player, ChatChannel.PRIVATE, player_name):
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
        """🆕 PHASE 4 - Détermine le résultat d'investigation du Sheriff (avec rôles neutres)"""
        # 🆕 Rôles suspects (Evil/Mafia + Serial Killer)
        suspicious_roles = [Role.WEREWOLF, Role.MAFIOSO, Role.BLACKMAILER, Role.CONSIGLIERE, Role.SERIAL_KILLER]
        
        # 🆕 Rôles immunisés (Godfather a immunité Sheriff dans SC2 Mafia)
        immune_roles = [Role.GODFATHER]
        
        if target_role in immune_roles:
            return SheriffResult.NOT_SUSPICIOUS  # Immunité Godfather
        elif target_role in suspicious_roles:
            return SheriffResult.SUSPICIOUS
        else:
            return SheriffResult.NOT_SUSPICIOUS  # Town + Survivor + Jester = Non suspects
    
    def _get_investigator_group(self, target_role):
        """🆕 PHASE 3 - Détermine le groupe d'investigation pour l'Investigator (avec rôles défensifs)"""
        # Mapping rôles vers groupes d'investigation
        role_groups = {
            # Town Roles
            Role.GUARD: InvestigationGroup.PROTECTORS,
            Role.SHERIFF: InvestigationGroup.INVESTIGATORS,
            Role.INVESTIGATOR: InvestigationGroup.INVESTIGATORS,
            Role.SEER: InvestigationGroup.INVESTIGATORS,
            Role.HUNTER: InvestigationGroup.KILLERS,
            Role.VILLAGER: InvestigationGroup.SUPPORT,
            Role.WITCH: InvestigationGroup.WITCHES,
            
            # 🆕 PHASE 3 - Rôles Défensifs Town
            Role.BODYGUARD: InvestigationGroup.PROTECTORS,
            Role.VETERAN: InvestigationGroup.KILLERS,     # Veteran peut tuer les attaquants
            Role.DOCTOR: InvestigationGroup.PROTECTORS,
            
            # 🆕 PHASE 4 - Rôles Neutres
            Role.SURVIVOR: InvestigationGroup.NEUTRALS,
            Role.SERIAL_KILLER: InvestigationGroup.KILLERS,  # SK est un tueur
            Role.JESTER: InvestigationGroup.NEUTRALS,
            
            # 🆕 PHASE 5 - Rôles Investigatifs Avancés
            Role.LOOKOUT: InvestigationGroup.PROTECTORS,     # Lookout protège par observation
            Role.SPY: InvestigationGroup.PROTECTORS,         # Spy protège par information
            Role.DETECTIVE: InvestigationGroup.INVESTIGATORS, # Detective est investigatif
            
            # 🆕 Mafia Roles - Tous dans le groupe MAFIA pour les cacher
            Role.WEREWOLF: InvestigationGroup.MAFIA,
            Role.GODFATHER: InvestigationGroup.MAFIA,
            Role.MAFIOSO: InvestigationGroup.MAFIA,
            Role.BLACKMAILER: InvestigationGroup.MAFIA,
            Role.CONSIGLIERE: InvestigationGroup.MAFIA
        }
        
        return role_groups.get(target_role, InvestigationGroup.SUPPORT)
    
    def _get_investigation_group_message(self, group):
        """🆕 PHASE 2 - Retourne le message d'investigation pour un groupe (avec groupe Mafia)"""
        group_messages = {
            InvestigationGroup.PROTECTORS: "Votre cible pourrait être un Bodyguard, Lookout ou Spy.",
            InvestigationGroup.INVESTIGATORS: "Votre cible pourrait être un Sheriff, Investigator ou Detective.",
            InvestigationGroup.KILLERS: "Votre cible pourrait être un Vigilante, Veteran ou Werewolf.",
            InvestigationGroup.SUPPORT: "Votre cible pourrait être un Citizen, Mayor ou Mason.",
            InvestigationGroup.WITCHES: "Votre cible pourrait être une Witch ou Witch Doctor.",
            InvestigationGroup.NEUTRALS: "Votre cible pourrait être un Survivor, Amnesiac ou Judge.",
            InvestigationGroup.MAFIA: "Votre cible pourrait être un Godfather, Mafioso ou Consigliere."
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
        
        game = self.games[game_id]
        return game.get('investigation_history', [])
    
    # 🆕 PHASE 1 - INVESTIGATION CONSIGLIERE
    def perform_consigliere_investigation(self, game_id, consigliere_name, target_name):
        """Investigation Consigliere - révèle le rôle exact (pour la Mafia)"""
        if game_id not in self.games:
            return False, "Partie introuvable"
        
        game = self.games[game_id]
        
        # Vérifications
        if consigliere_name not in game['players']:
            return False, "Consigliere introuvable"
        
        if target_name not in game['players']:
            return False, "Cible introuvable"
        
        consigliere = game['players'][consigliere_name]
        target = game['players'][target_name]
        
        if consigliere['role'] != Role.CONSIGLIERE:
            return False, "Seul le Consigliere peut utiliser cette investigation"
        
        if not consigliere['alive']:
            return False, "Les morts ne peuvent pas enquêter"
        
        if not target['alive']:
            return False, "Impossible d'enquêter sur les morts"
        
        if target_name == consigliere_name:
            return False, "Vous ne pouvez pas enquêter sur vous-même"
        
        # Révéler le rôle exact (pas d'immunité pour Consigliere)
        target_role = target['role']
        
        # Créer le résultat d'investigation
        investigation_result = {
            'investigator': consigliere_name,
            'target': target_name,
            'result': target_role.value,
            'result_message': f"{target_name} est exactement : {self._get_role_display_name(target_role)}",
            'timestamp': datetime.now().isoformat(),
            'night': game['day_count'],
            'type': 'consigliere'
        }
        
        # Sauvegarder le résultat
        if consigliere_name not in game['investigation_results']:
            game['investigation_results'][consigliere_name] = []
        
        game['investigation_results'][consigliere_name].append(investigation_result)
        
        # Ajouter à l'historique global
        game['investigation_history'].append(investigation_result)
        
        return True, investigation_result['result_message']
    
    def _get_role_display_name(self, role):
        """Retourne le nom d'affichage d'un rôle"""
        role_names = {
            Role.VILLAGER: "Villageois",
            Role.SEER: "Voyant", 
            Role.WITCH: "Sorcière",
            Role.GUARD: "Garde",
            Role.HUNTER: "Chasseur",
            Role.SHERIFF: "Sheriff",
            Role.INVESTIGATOR: "Investigateur",
            Role.WEREWOLF: "Loup-Garou",
            Role.GODFATHER: "Parrain",
            Role.MAFIOSO: "Mafioso", 
            Role.BLACKMAILER: "Maître-Chanteur",
            Role.CONSIGLIERE: "Conseiller"
        }
        return role_names.get(role, role.value)
    
    # 🆕 PHASE 5 - INVESTIGATIONS AVANCÉES
    def perform_detective_investigation(self, game_id, detective_name, target_name):
        """Investigation Detective - révèle des informations avec historique et déductions"""
        if game_id not in self.games:
            return False, "Partie introuvable"
        
        game = self.games[game_id]
        
        # Vérifications
        if detective_name not in game['players']:
            return False, "Detective introuvable"
        
        if target_name not in game['players']:
            return False, "Cible introuvable"
        
        detective = game['players'][detective_name]
        target = game['players'][target_name]
        
        if detective['role'] != Role.DETECTIVE:
            return False, "Seul le Detective peut utiliser cette investigation"
        
        if not detective['alive']:
            return False, "Les morts ne peuvent pas enquêter"
        
        if not target['alive']:
            return False, "Impossible d'enquêter sur les morts"
        
        if target_name == detective_name:
            return False, "Vous ne pouvez pas enquêter sur vous-même"
        
        # Investigation Detective combine Sheriff + Investigator + historique
        target_role = target['role']
        
        # Résultat Sheriff
        sheriff_result = self._get_sheriff_result(Role.SHERIFF, target_role)
        sheriff_text = "SUSPECT" if sheriff_result == SheriffResult.SUSPICIOUS else "NON SUSPECT"
        
        # Résultat Investigator  
        investigator_group = self._get_investigator_group(target_role)
        investigator_text = self._get_investigation_group_message(investigator_group)
        
        # Déduction basée sur l'historique
        detective_results = detective.get('detective_results', [])
        previous_investigations = len(detective_results)
        
        # Bonus d'information selon l'expérience
        bonus_info = ""
        if previous_investigations >= 2:
            bonus_info = f" | Confiance élevée (Investigation #{previous_investigations + 1})"
        elif previous_investigations >= 1:
            bonus_info = f" | Confiance modérée (Investigation #{previous_investigations + 1})"
        else:
            bonus_info = " | Première investigation"
        
        # Message complet
        full_message = f"🕵️ ANALYSE DETECTIVE de {target_name}:\n• Sheriff: {sheriff_text}\n• Profil: {investigator_text}\n• Statut: {bonus_info}"
        
        # Créer le résultat d'investigation
        investigation_result = {
            'investigator': detective_name,
            'target': target_name,
            'sheriff_result': sheriff_result.value,
            'investigator_group': investigator_group.value,
            'full_analysis': full_message,
            'investigation_number': previous_investigations + 1,
            'timestamp': datetime.now().isoformat(),
            'night': game['day_count'],
            'type': 'detective'
        }
        
        # Sauvegarder le résultat
        if 'detective_results' not in detective:
            detective['detective_results'] = []
        detective['detective_results'].append(investigation_result)
        
        if detective_name not in game['investigation_results']:
            game['investigation_results'][detective_name] = []
        game['investigation_results'][detective_name].append(investigation_result)
        
        # Ajouter à l'historique global
        game['investigation_history'].append(investigation_result)
        
        return True, full_message

# Global game engine instance
game_engine = GameEngine() 