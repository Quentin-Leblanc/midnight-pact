from flask import Blueprint, request, jsonify
from src.models.game import db, Game, Player
from src.game_engine import game_engine
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques de la base de données"""
    try:
        total_games = Game.query.count()
        total_players = Player.query.count()
        
        # Statistiques par statut
        status_stats = db.session.query(
            Game.status, 
            db.func.count(Game.id)
        ).group_by(Game.status).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_games': total_games,
                'total_players': total_players,
                'status_breakdown': [
                    {'status': status, 'count': count} 
                    for status, count in status_stats
                ]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/clear-all', methods=['POST'])
def clear_all_history():
    """Effacer complètement l'historique des parties"""
    try:
        # Compter avant suppression
        game_count = Game.query.count()
        player_count = Player.query.count()
        
        # Supprimer tous les joueurs et parties
        Player.query.delete()
        Game.query.delete()
        db.session.commit()
        
        # Vider aussi la mémoire du game engine
        game_engine.games.clear()
        
        return jsonify({
            'success': True,
            'message': f'Historique effacé : {game_count} parties et {player_count} entrées joueur supprimées',
            'deleted': {
                'games': game_count,
                'players': player_count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/clear-finished', methods=['POST'])
def clear_finished_games():
    """Effacer seulement les parties terminées"""
    try:
        # Trouver les parties terminées
        finished_games = Game.query.filter_by(status='finished').all()
        finished_count = len(finished_games)
        
        if finished_count == 0:
            return jsonify({
                'success': True,
                'message': 'Aucune partie terminée à supprimer'
            })
        
        # Compter les joueurs associés
        finished_game_ids = [game.id for game in finished_games]
        player_count = Player.query.filter(Player.game_id.in_(finished_game_ids)).count()
        
        # Supprimer les joueurs des parties terminées
        Player.query.filter(Player.game_id.in_(finished_game_ids)).delete(synchronize_session=False)
        
        # Supprimer les parties terminées
        Game.query.filter_by(status='finished').delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Parties terminées supprimées : {finished_count} parties et {player_count} entrées joueur',
            'deleted': {
                'games': finished_count,
                'players': player_count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/clear-old', methods=['POST'])
def clear_old_games():
    """Effacer les parties anciennes (plus de X jours)"""
    try:
        # Récupérer le nombre de jours depuis la requête (défaut 7)
        days = request.json.get('days', 7) if request.json else 7
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Trouver les parties anciennes
        old_games = Game.query.filter(Game.created_at < cutoff_date).all()
        old_count = len(old_games)
        
        if old_count == 0:
            return jsonify({
                'success': True,
                'message': f'Aucune partie plus ancienne que {days} jours'
            })
        
        # Compter les joueurs associés
        old_game_ids = [game.id for game in old_games]
        player_count = Player.query.filter(Player.game_id.in_(old_game_ids)).count()
        
        # Supprimer les joueurs des parties anciennes
        Player.query.filter(Player.game_id.in_(old_game_ids)).delete(synchronize_session=False)
        
        # Supprimer les parties anciennes
        Game.query.filter(Game.created_at < cutoff_date).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Parties anciennes supprimées : {old_count} parties et {player_count} entrées joueur (plus de {days} jours)',
            'deleted': {
                'games': old_count,
                'players': player_count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/backup', methods=['POST'])
def create_backup():
    """Créer une sauvegarde de la base de données"""
    try:
        import shutil
        
        # Chemin de la base de données
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
        
        if not os.path.exists(db_path):
            return jsonify({'success': False, 'error': 'Base de données non trouvée'}), 404
        
        # Créer le nom de sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{db_path}.backup_{timestamp}"
        
        # Copier la base de données
        shutil.copy2(db_path, backup_path)
        
        return jsonify({
            'success': True,
            'message': 'Sauvegarde créée avec succès',
            'backup_path': backup_path,
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 