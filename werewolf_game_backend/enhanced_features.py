#!/usr/bin/env python3
"""
Fonctionnalités avancées pour enrichir le jeu Loup-Garou
Inspiré des mécaniques de SC2 Mafia et des variantes modernes du Loup-Garou
"""

import random
from datetime import datetime, timedelta
from src.game_engine import game_engine

class EnhancedGameFeatures:
    """Fonctionnalités avancées pour le jeu Loup-Garou"""
    
    def __init__(self):
        self.achievements = {}
        self.game_statistics = {}
        self.random_events = [
            {
                'name': 'Eclipse Lunaire',
                'description': 'La lune disparaît ! Cette nuit, les loups-garous ne peuvent pas tuer.',
                'effect': 'block_werewolf_kill',
                'probability': 0.05
            },
            {
                'name': 'Pleine Lune',
                'description': 'La pleine lune renforce les créatures ! Les loups peuvent tuer 2 personnes.',
                'effect': 'double_werewolf_kill',
                'probability': 0.03
            },
            {
                'name': 'Brouillard Mystique',
                'description': 'Un épais brouillard couvre le village. Les actions nocturnes ont 50% de chance d\'échouer.',
                'effect': 'random_failure',
                'probability': 0.08
            },
            {
                'name': 'Nuit Calme',
                'description': 'La paix règne sur le village. Tous les joueurs regagnent un peu d\'espoir.',
                'effect': 'peaceful_night',
                'probability': 0.1
            },
            {
                'name': 'Cauchemar Collectif',
                'description': 'Des cauchemars hantent le village. Le vote du lendemain est secret.',
                'effect': 'secret_voting',
                'probability': 0.06
            }
        ]
    
    def trigger_random_event(self, game_id):
        """Déclencher un événement aléatoire"""
        if game_id not in game_engine.games:
            return None
        
        game = game_engine.games[game_id]
        
        # Chance d'événement basée sur le jour (plus fréquent tard dans la partie)
        base_chance = 0.15 + (game.get('day_count', 1) * 0.02)
        
        if random.random() < base_chance:
            event = random.choices(
                self.random_events,
                weights=[e['probability'] for e in self.random_events],
                k=1
            )[0]
            
            # Appliquer l'effet
            self._apply_event_effect(game_id, event)
            
            # Ajouter à l'historique
            game['game_history'].append({
                'type': 'random_event',
                'phase': game['phase'].value if hasattr(game['phase'], 'value') else str(game['phase']),
                'day': game.get('day_count', 1),
                'event_name': event['name'],
                'description': f"🎭 {event['name']}: {event['description']}"
            })
            
            return event
        
        return None
    
    def _apply_event_effect(self, game_id, event):
        """Appliquer l'effet d'un événement"""
        if game_id not in game_engine.games:
            return
        
        game = game_engine.games[game_id]
        effect = event['effect']
        
        if effect == 'block_werewolf_kill':
            game['blocked_werewolf_kill'] = True
        elif effect == 'double_werewolf_kill':
            game['double_werewolf_kill'] = True
        elif effect == 'random_failure':
            game['random_failure_chance'] = 0.5
        elif effect == 'peaceful_night':
            # Réinitialiser les votes et réduire les tensions
            for player in game['players'].values():
                player['has_voted'] = False
                player['vote_target'] = None
        elif effect == 'secret_voting':
            game['secret_voting'] = True
    
    def generate_player_tips(self, game_id, player_name):
        """Générer des conseils stratégiques pour le joueur"""
        if game_id not in game_engine.games:
            return []
        
        game = game_engine.games[game_id]
        if player_name not in game['players']:
            return []
        
        player = game['players'][player_name]
        role = player['role']
        phase = game['phase']
        day_count = game.get('day_count', 1)
        
        tips = []
        
        # Conseils selon le rôle
        if role.value == 'villager':
            tips.extend([
                "Observez les comportements suspects et les incohérences.",
                "Participez activement aux discussions pour identifier les loups.",
                "Méfiez-vous des joueurs trop silencieux ou trop bavards."
            ])
        elif role.value == 'werewolf':
            tips.extend([
                "Restez discret et évitez d'attirer l'attention.",
                "Coordonnez-vous avec vos équipiers loups-garous.",
                "Accusez subtilement d'autres joueurs pour semer la confusion."
            ])
        elif role.value == 'seer':
            tips.extend([
                "Utilisez vos investigations avec parcimonie.",
                "Ne révélez votre rôle qu'en dernier recours.",
                "Gardez vos informations secrètes jusqu'au bon moment."
            ])
        elif role.value == 'witch':
            tips.extend([
                "Conservez vos potions pour les moments critiques.",
                "La potion de poison peut éliminer un loup-garou confirmé.",
                "Utilisez la guérison pour sauver un joueur clé."
            ])
        
        # Conseils selon la phase
        if phase.value == 'day':
            tips.append("C'est le moment de partager vos informations et de débattre.")
        elif phase.value == 'night':
            tips.append("Réfléchissez bien à vos actions nocturnes.")
        elif phase.value == 'voting':
            tips.append("Analysez tous les indices avant de voter.")
        
        # Conseils selon le moment de la partie
        if day_count >= 3:
            tips.append("En fin de partie, chaque vote compte double !")
        
        return tips[:3]  # Limiter à 3 conseils
    
    def calculate_player_stats(self, game_id, player_name):
        """Calculer les statistiques du joueur"""
        if game_id not in game_engine.games:
            return {}
        
        game = game_engine.games[game_id]
        if player_name not in game['players']:
            return {}
        
        player = game['players'][player_name]
        
        # Calculer les stats
        stats = {
            'survival_days': game.get('day_count', 1) if player['alive'] else 0,
            'messages_sent': len([msg for msg in game.get('chat_messages', []) 
                                if msg.get('player_name') == player_name]),
            'votes_cast': 1 if player.get('has_voted') else 0,
            'actions_performed': 1 if player.get('night_action_used') else 0,
            'role': player['role'].value if hasattr(player['role'], 'value') else str(player['role']),
            'status': 'Vivant' if player['alive'] else 'Mort'
        }
        
        return stats
    
    def generate_end_game_report(self, game_id):
        """Générer un rapport de fin de partie"""
        if game_id not in game_engine.games:
            return {}
        
        game = game_engine.games[game_id]
        
        # Statistiques de la partie
        total_players = len(game['players'])
        total_days = game.get('day_count', 1)
        winner = game.get('winner')
        
        # MVP (Most Valuable Player)
        mvp = self._calculate_mvp(game)
        
        # Statistiques par rôle
        role_stats = {}
        for player_name, player in game['players'].items():
            role = player['role'].value if hasattr(player['role'], 'value') else str(player['role'])
            if role not in role_stats:
                role_stats[role] = {'total': 0, 'survived': 0}
            role_stats[role]['total'] += 1
            if player['alive']:
                role_stats[role]['survived'] += 1
        
        # Moments clés
        key_moments = [event for event in game.get('game_history', []) 
                      if event.get('type') in ['elimination', 'random_event']]
        
        report = {
            'game_duration': f"{total_days} jours",
            'total_players': total_players,
            'winner_team': winner,
            'mvp': mvp,
            'role_statistics': role_stats,
            'key_moments': key_moments[-5:],  # 5 derniers moments clés
            'total_messages': len(game.get('chat_messages', [])),
            'total_eliminations': len([e for e in game.get('game_history', []) 
                                     if e.get('type') == 'elimination'])
        }
        
        return report
    
    def _calculate_mvp(self, game):
        """Calculer le joueur le plus précieux"""
        if not game['players']:
            return None
        
        mvp_score = 0
        mvp_player = None
        
        for player_name, player in game['players'].items():
            score = 0
            
            # Points pour la survie
            if player['alive']:
                score += 3
            
            # Points pour les messages (participation)
            messages = len([msg for msg in game.get('chat_messages', []) 
                          if msg.get('player_name') == player_name])
            score += min(messages, 5)  # Max 5 points pour les messages
            
            # Points pour les actions
            if player.get('night_action_used'):
                score += 2
            
            # Points bonus selon le rôle
            role = player['role'].value if hasattr(player['role'], 'value') else str(player['role'])
            if role == 'seer' and player.get('night_action_used'):
                score += 3  # Bonus pour le voyant actif
            elif role == 'witch' and (player.get('witch_heal_used') or player.get('witch_poison_used')):
                score += 2  # Bonus pour la sorcière active
            
            if score > mvp_score:
                mvp_score = score
                mvp_player = player_name
        
        return mvp_player
    
    def add_achievement(self, player_name, achievement_type, description):
        """Ajouter un succès à un joueur"""
        if player_name not in self.achievements:
            self.achievements[player_name] = []
        
        achievement = {
            'type': achievement_type,
            'description': description,
            'date': datetime.now().isoformat(),
            'icon': self._get_achievement_icon(achievement_type)
        }
        
        self.achievements[player_name].append(achievement)
        return achievement
    
    def _get_achievement_icon(self, achievement_type):
        """Obtenir l'icône d'un succès"""
        icons = {
            'first_game': '🎮',
            'survivor': '💪',
            'detective': '🔍',
            'strategist': '🧠',
            'communicator': '💬',
            'werewolf_hunter': '🏹',
            'master_manipulator': '🎭',
            'team_player': '🤝',
            'lone_wolf': '🐺',
            'lucky': '🍀'
        }
        return icons.get(achievement_type, '⭐')

# Instance globale
enhanced_features = EnhancedGameFeatures() 