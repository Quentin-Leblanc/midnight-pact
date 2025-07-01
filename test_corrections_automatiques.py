#!/usr/bin/env python3
"""
Script de test automatisé pour valider les corrections de synchronisation
du jeu Midnight Pact
"""

import requests
import time
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"

class TestCorrections:
    def __init__(self):
        self.results = []
        self.game_id = None
        
    def log_test(self, test_name, success, message, details=None):
        """Enregistrer le résultat d'un test"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_server_connection(self):
        """Test 1: Vérifier que le serveur backend fonctionne"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Connexion Serveur", True, "Serveur backend accessible")
                return True
            else:
                self.log_test("Connexion Serveur", False, f"Code erreur: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Connexion Serveur", False, f"Erreur de connexion: {str(e)}")
            return False
    
    def test_game_creation(self):
        """Test 2: Créer une nouvelle partie"""
        try:
            payload = {
                "name": "Test Corrections",
                "max_players": 8
            }
            response = requests.post(f"{API_BASE}/games", json=payload, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                self.game_id = data.get('game_id')
                self.log_test("Création Partie", True, f"Partie créée: {self.game_id}")
                return True
            else:
                self.log_test("Création Partie", False, f"Échec création: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Création Partie", False, f"Erreur: {str(e)}")
            return False
    
    def test_add_players(self):
        """Test 3: Ajouter des joueurs à la partie"""
        if not self.game_id:
            self.log_test("Ajout Joueurs", False, "Pas de game_id disponible")
            return False
        
        players = ["TestPlayer1", "TestPlayer2", "TestPlayer3", "TestPlayer4", "TestPlayer5", "TestPlayer6"]
        added_count = 0
        
        for player in players:
            try:
                payload = {"player_name": player}
                response = requests.post(f"{API_BASE}/games/{self.game_id}/join", json=payload, timeout=5)
                
                if response.status_code == 200:
                    added_count += 1
                else:
                    print(f"   Échec ajout {player}: {response.status_code}")
            except Exception as e:
                print(f"   Erreur ajout {player}: {str(e)}")
        
        if added_count >= 4:
            self.log_test("Ajout Joueurs", True, f"{added_count} joueurs ajoutés", 
                         {"joueurs_requis": 4, "joueurs_ajoutés": added_count})
            return True
        else:
            self.log_test("Ajout Joueurs", False, f"Seulement {added_count} joueurs ajoutés")
            return False
    
    def test_game_start_lobby_phase(self):
        """Test 4: Démarrer la partie et vérifier la phase LOBBY"""
        if not self.game_id:
            self.log_test("Phase Lobby", False, "Pas de game_id disponible")
            return False
        
        try:
            # Démarrer la partie
            response = requests.post(f"{API_BASE}/games/{self.game_id}/start", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Phase Lobby", False, f"Échec démarrage: {response.status_code}")
                return False
            
            # Attendre 1 seconde puis vérifier l'état
            time.sleep(1)
            
            # Vérifier l'état de la partie
            state_response = requests.get(f"{API_BASE}/games/{self.game_id}/state", timeout=5)
            
            if state_response.status_code == 200:
                game_state = state_response.json()
                phase = game_state.get('phase')
                status = game_state.get('status')
                winner = game_state.get('winner')
                
                # Vérifications critiques
                if winner:
                    self.log_test("Phase Lobby", False, f"VICTOIRE INSTANTANÉE DÉTECTÉE: {winner}",
                                 {"phase": phase, "status": status})
                    return False
                
                if phase == 'lobby':
                    self.log_test("Phase Lobby", True, "Phase lobby correctement activée",
                                 {"phase": phase, "status": status, "pas_de_victoire": True})
                    return True
                else:
                    self.log_test("Phase Lobby", False, f"Phase incorrecte: {phase} (attendu: lobby)",
                                 {"phase_actuelle": phase, "phase_attendue": "lobby"})
                    return False
            else:
                self.log_test("Phase Lobby", False, f"Impossible d'obtenir l'état: {state_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Phase Lobby", False, f"Erreur: {str(e)}")
            return False
    
    def test_role_assignment(self):
        """Test 5: Vérifier l'attribution des rôles"""
        if not self.game_id:
            self.log_test("Attribution Rôles", False, "Pas de game_id disponible")
            return False
        
        try:
            # Vérifier les rôles attribués
            role_response = requests.get(f"{API_BASE}/games/{self.game_id}/player/TestPlayer1/role", timeout=5)
            
            if role_response.status_code == 200:
                role_data = role_response.json()
                role = role_data.get('role')
                alive = role_data.get('alive')
                
                if role and alive:
                    self.log_test("Attribution Rôles", True, f"Rôle attribué: {role}",
                                 {"rôle": role, "vivant": alive})
                    return True
                else:
                    self.log_test("Attribution Rôles", False, "Données de rôle incomplètes")
                    return False
            else:
                self.log_test("Attribution Rôles", False, f"Impossible d'obtenir le rôle: {role_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Attribution Rôles", False, f"Erreur: {str(e)}")
            return False
    
    def test_lobby_to_night_transition(self):
        """Test 6: Vérifier la transition LOBBY → NIGHT"""
        if not self.game_id:
            self.log_test("Transition Lobby→Nuit", False, "Pas de game_id disponible")
            return False
        
        try:
            print("   Attente de la transition lobby → nuit (12 secondes)...")
            
            # Attendre la fin de la phase lobby (10s + marge)
            time.sleep(12)
            
            # Vérifier que la phase est passée à NIGHT
            state_response = requests.get(f"{API_BASE}/games/{self.game_id}/state", timeout=5)
            
            if state_response.status_code == 200:
                game_state = state_response.json()
                phase = game_state.get('phase')
                day_count = game_state.get('day_count', 0)
                winner = game_state.get('winner')
                
                # Vérifications critiques
                if winner:
                    self.log_test("Transition Lobby→Nuit", False, f"VICTOIRE PENDANT TRANSITION: {winner}",
                                 {"phase": phase, "jour": day_count})
                    return False
                
                if phase == 'night':
                    self.log_test("Transition Lobby→Nuit", True, "Transition réussie vers la nuit",
                                 {"phase": phase, "jour": day_count, "pas_de_victoire": True})
                    return True
                elif phase == 'lobby':
                    self.log_test("Transition Lobby→Nuit", False, "Encore en phase lobby (timer non écoulé?)",
                                 {"phase": phase, "durée_attendue": "10s"})
                    return False
                else:
                    self.log_test("Transition Lobby→Nuit", False, f"Phase inattendue: {phase}",
                                 {"phase_actuelle": phase, "phase_attendue": "night"})
                    return False
            else:
                self.log_test("Transition Lobby→Nuit", False, f"Erreur état: {state_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Transition Lobby→Nuit", False, f"Erreur: {str(e)}")
            return False
    
    def test_game_flow_stability(self):
        """Test 7: Vérifier la stabilité du flux de jeu"""
        if not self.game_id:
            self.log_test("Stabilité Flux", False, "Pas de game_id disponible")
            return False
        
        try:
            # Vérifier l'état plusieurs fois pour détecter des incohérences
            states = []
            
            for i in range(3):
                response = requests.get(f"{API_BASE}/games/{self.game_id}/state", timeout=5)
                if response.status_code == 200:
                    state = response.json()
                    states.append({
                        'phase': state.get('phase'),
                        'status': state.get('status'),
                        'winner': state.get('winner'),
                        'day_count': state.get('day_count')
                    })
                time.sleep(2)
            
            # Analyser la cohérence
            if len(states) == 3:
                # Vérifier qu'il n'y a pas de victoire soudaine
                winners = [s['winner'] for s in states if s['winner']]
                if winners:
                    self.log_test("Stabilité Flux", False, f"Victoire inattendue détectée: {winners[0]}",
                                 {"états_analysés": 3, "victoires": len(winners)})
                    return False
                
                # Vérifier la cohérence des phases
                phases = [s['phase'] for s in states]
                stable_phases = len(set(phases)) <= 2  # Autorise 1 transition maximum
                
                if stable_phases:
                    self.log_test("Stabilité Flux", True, "Flux de jeu stable",
                                 {"phases_observées": phases, "pas_de_victoire": True})
                    return True
                else:
                    self.log_test("Stabilité Flux", False, f"Phases instables: {phases}")
                    return False
            else:
                self.log_test("Stabilité Flux", False, "Impossible d'obtenir tous les états")
                return False
                
        except Exception as e:
            self.log_test("Stabilité Flux", False, f"Erreur: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests de validation"""
        print("🧪 DÉBUT DES TESTS DE VALIDATION DES CORRECTIONS")
        print("=" * 60)
        
        # Séquence de tests
        tests = [
            self.test_server_connection,
            self.test_game_creation,
            self.test_add_players,
            self.test_game_start_lobby_phase,
            self.test_role_assignment,
            self.test_lobby_to_night_transition,
            self.test_game_flow_stability
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                print()  # Ligne vide entre les tests
            except Exception as e:
                self.log_test(test_func.__name__, False, f"Exception: {str(e)}")
                print()
        
        # Résumé final
        print("=" * 60)
        print(f"🎯 RÉSULTATS FINAUX: {passed}/{total} tests réussis")
        
        if passed == total:
            print("✅ TOUS LES TESTS SONT PASSÉS - CORRECTIONS VALIDÉES !")
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ - RÉVISION NÉCESSAIRE")
        
        return passed == total
    
    def generate_report(self):
        """Générer un rapport détaillé des tests"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r['success']]),
            'failed_tests': len([r for r in self.results if not r['success']]),
            'game_id': self.game_id,
            'results': self.results
        }
        
        return report

def main():
    """Fonction principale"""
    tester = TestCorrections()
    
    try:
        success = tester.run_all_tests()
        
        # Générer le rapport
        report = tester.generate_report()
        
        # Sauvegarder le rapport
        with open('test_corrections_rapport.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé sauvegardé: test_corrections_rapport.json")
        
        if success:
            print("\n🎉 VALIDATION COMPLÈTE - LE JEU FONCTIONNE CORRECTEMENT !")
        else:
            print("\n⚠️  VALIDATION PARTIELLE - QUELQUES PROBLÈMES DÉTECTÉS")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\n💥 Erreur critique: {str(e)}")

if __name__ == "__main__":
    main()