#!/usr/bin/env python3
"""
Script pour effacer l'historique des parties du jeu Loup-Garou
"""
import os
import sys
import sqlite3
from datetime import datetime

# Ajouter le path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def clear_database():
    """Vide complètement la base de données"""
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée !")
        return False
    
    try:
        # Créer une sauvegarde avant suppression
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copier la base actuelle
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Sauvegarde créée : {backup_path}")
        
        # Se connecter et vider les tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les enregistrements avant suppression
        cursor.execute("SELECT COUNT(*) FROM game")
        game_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM player")
        player_count = cursor.fetchone()[0]
        
        print(f"📊 Avant suppression : {game_count} parties, {player_count} joueurs")
        
        # Vider les tables
        cursor.execute("DELETE FROM player")
        cursor.execute("DELETE FROM game")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('game', 'player')")
        
        conn.commit()
        conn.close()
        
        print("✅ Historique des parties effacé avec succès !")
        print("🔄 Redémarrez le serveur pour vider la mémoire cache")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        return False

def clear_finished_games_only():
    """Efface seulement les parties terminées"""
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée !")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les parties terminées
        cursor.execute("SELECT COUNT(*) FROM game WHERE status = 'finished'")
        finished_count = cursor.fetchone()[0]
        
        print(f"📊 Parties terminées à supprimer : {finished_count}")
        
        if finished_count == 0:
            print("ℹ️ Aucune partie terminée à supprimer")
            conn.close()
            return True
        
        # Supprimer les joueurs des parties terminées
        cursor.execute("""
            DELETE FROM player 
            WHERE game_id IN (SELECT id FROM game WHERE status = 'finished')
        """)
        
        # Supprimer les parties terminées
        cursor.execute("DELETE FROM game WHERE status = 'finished'")
        
        conn.commit()
        conn.close()
        
        print("✅ Parties terminées supprimées avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        return False

def show_statistics():
    """Affiche les statistiques de la base de données"""
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée !")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        cursor.execute("SELECT COUNT(*) FROM game")
        total_games = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM player")
        total_players = cursor.fetchone()[0]
        
        # Statistiques par statut
        cursor.execute("SELECT status, COUNT(*) FROM game GROUP BY status")
        status_stats = cursor.fetchall()
        
        print("📊 === STATISTIQUES DE LA BASE DE DONNÉES ===")
        print(f"🎮 Total des parties : {total_games}")
        print(f"👥 Total des entrées joueurs : {total_players}")
        print("\n📈 Répartition par statut :")
        for status, count in status_stats:
            print(f"   • {status}: {count} parties")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")

def main():
    """Menu principal"""
    print("🐺 === GESTIONNAIRE D'HISTORIQUE LOUP-GAROU ===\n")
    
    while True:
        print("Que voulez-vous faire ?")
        print("1. 📊 Voir les statistiques")
        print("2. 🧹 Effacer TOUT l'historique")
        print("3. 🗂️ Effacer seulement les parties terminées")
        print("4. ❌ Quitter")
        
        choice = input("\nVotre choix (1-4) : ").strip()
        
        if choice == "1":
            show_statistics()
        elif choice == "2":
            confirm = input("⚠️ Êtes-vous sûr de vouloir effacer TOUT l'historique ? (oui/non) : ").strip().lower()
            if confirm in ['oui', 'o', 'yes', 'y']:
                clear_database()
            else:
                print("❌ Annulé")
        elif choice == "3":
            clear_finished_games_only()
        elif choice == "4":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main() 