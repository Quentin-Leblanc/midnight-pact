#!/bin/bash

# Script de test des corrections - Version cURL
# Teste les corrections de synchronisation du jeu Midnight Pact

API_BASE="http://localhost:5000/api"
GAME_ID=""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log_test() {
    local test_name="$1"
    local success="$2"
    local message="$3"
    
    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name: $message"
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name: $message"
    fi
}

# Test 1: Vérifier la connexion au serveur
test_server_connection() {
    echo "🔍 Test 1: Connexion au serveur backend..."
    
    # Tester si le serveur répond
    if curl -s -f "$API_BASE/health" > /dev/null 2>&1; then
        log_test "Connexion Serveur" "true" "Serveur backend accessible"
        return 0
    else
        # Fallback : tester une route basique 
        if curl -s -f "$API_BASE/games" > /dev/null 2>&1; then
            log_test "Connexion Serveur" "true" "Serveur backend accessible (route games)"
            return 0
        else
            log_test "Connexion Serveur" "false" "Serveur backend inaccessible"
            return 1
        fi
    fi
}

# Test 2: Créer une partie
test_game_creation() {
    echo "🔍 Test 2: Création d'une nouvelle partie..."
    
    # Créer une partie de test
    response=$(curl -s -X POST "$API_BASE/games" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Corrections", "max_players": 8}' \
        -w "HTTP_STATUS:%{http_code}")
    
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        # Extraire le game_id
        GAME_ID=$(echo "$response_body" | grep -o '"game_id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$GAME_ID" ]; then
            log_test "Création Partie" "true" "Partie créée: $GAME_ID"
            return 0
        else
            log_test "Création Partie" "false" "Game ID non trouvé dans la réponse"
            return 1
        fi
    else
        log_test "Création Partie" "false" "Échec création (HTTP $http_code)"
        return 1
    fi
}

# Test 3: Ajouter des joueurs
test_add_players() {
    echo "🔍 Test 3: Ajout de joueurs à la partie..."
    
    if [ -z "$GAME_ID" ]; then
        log_test "Ajout Joueurs" "false" "Pas de game_id disponible"
        return 1
    fi
    
    players=("TestPlayer1" "TestPlayer2" "TestPlayer3" "TestPlayer4" "TestPlayer5" "TestPlayer6")
    added_count=0
    
    for player in "${players[@]}"; do
        response=$(curl -s -X POST "$API_BASE/games/$GAME_ID/join" \
            -H "Content-Type: application/json" \
            -d "{\"player_name\": \"$player\"}" \
            -w "HTTP_STATUS:%{http_code}")
        
        http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
        
        if [ "$http_code" = "200" ]; then
            ((added_count++))
        else
            echo "   Échec ajout $player: HTTP $http_code"
        fi
    done
    
    if [ $added_count -ge 4 ]; then
        log_test "Ajout Joueurs" "true" "$added_count joueurs ajoutés (minimum: 4)"
        return 0
    else
        log_test "Ajout Joueurs" "false" "Seulement $added_count joueurs ajoutés"
        return 1
    fi
}

# Test 4: Démarrer la partie et vérifier la phase LOBBY
test_game_start_lobby_phase() {
    echo "🔍 Test 4: Démarrage de la partie et vérification phase LOBBY..."
    
    if [ -z "$GAME_ID" ]; then
        log_test "Phase Lobby" "false" "Pas de game_id disponible"
        return 1
    fi
    
    # Démarrer la partie
    response=$(curl -s -X POST "$API_BASE/games/$GAME_ID/start" \
        -H "Content-Type: application/json" \
        -w "HTTP_STATUS:%{http_code}")
    
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_code" != "200" ]; then
        log_test "Phase Lobby" "false" "Échec démarrage (HTTP $http_code)"
        return 1
    fi
    
    # Attendre 1 seconde puis vérifier l'état
    echo "   Attente 1 seconde..."
    sleep 1
    
    # Vérifier l'état de la partie
    state_response=$(curl -s "$API_BASE/games/$GAME_ID/state" -w "HTTP_STATUS:%{http_code}")
    state_http_code=$(echo "$state_response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    state_body=$(echo "$state_response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$state_http_code" = "200" ]; then
        # Extraire les informations importantes
        phase=$(echo "$state_body" | grep -o '"phase":"[^"]*"' | cut -d'"' -f4)
        status=$(echo "$state_body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        winner=$(echo "$state_body" | grep -o '"winner":"[^"]*"' | cut -d'"' -f4)
        
        # VÉRIFICATION CRITIQUE: Pas de victoire instantanée
        if [ -n "$winner" ] && [ "$winner" != "null" ]; then
            log_test "Phase Lobby" "false" "🚨 VICTOIRE INSTANTANÉE DÉTECTÉE: $winner"
            echo "   Phase: $phase, Status: $status"
            return 1
        fi
        
        # Vérifier que la phase est bien 'lobby'
        if [ "$phase" = "lobby" ]; then
            log_test "Phase Lobby" "true" "Phase lobby correctement activée (pas de victoire instantanée)"
            echo "   Phase: $phase, Status: $status"
            return 0
        else
            log_test "Phase Lobby" "false" "Phase incorrecte: $phase (attendu: lobby)"
            echo "   Status: $status"
            return 1
        fi
    else
        log_test "Phase Lobby" "false" "Impossible d'obtenir l'état (HTTP $state_http_code)"
        return 1
    fi
}

# Test 5: Vérifier la transition LOBBY → NIGHT
test_lobby_to_night_transition() {
    echo "🔍 Test 5: Vérification transition LOBBY → NIGHT..."
    
    if [ -z "$GAME_ID" ]; then
        log_test "Transition Lobby→Nuit" "false" "Pas de game_id disponible"
        return 1
    fi
    
    echo "   Attente de la transition lobby → nuit (12 secondes)..."
    sleep 12
    
    # Vérifier que la phase est passée à NIGHT
    state_response=$(curl -s "$API_BASE/games/$GAME_ID/state" -w "HTTP_STATUS:%{http_code}")
    state_http_code=$(echo "$state_response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    state_body=$(echo "$state_response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$state_http_code" = "200" ]; then
        phase=$(echo "$state_body" | grep -o '"phase":"[^"]*"' | cut -d'"' -f4)
        day_count=$(echo "$state_body" | grep -o '"day_count":[0-9]*' | cut -d: -f2)
        winner=$(echo "$state_body" | grep -o '"winner":"[^"]*"' | cut -d'"' -f4)
        
        # VÉRIFICATION CRITIQUE: Pas de victoire pendant la transition
        if [ -n "$winner" ] && [ "$winner" != "null" ]; then
            log_test "Transition Lobby→Nuit" "false" "🚨 VICTOIRE PENDANT TRANSITION: $winner"
            echo "   Phase: $phase, Jour: $day_count"
            return 1
        fi
        
        if [ "$phase" = "night" ]; then
            log_test "Transition Lobby→Nuit" "true" "Transition réussie vers la nuit"
            echo "   Phase: $phase, Jour: $day_count, Pas de victoire: ✓"
            return 0
        elif [ "$phase" = "lobby" ]; then
            log_test "Transition Lobby→Nuit" "false" "Encore en phase lobby (timer non écoulé?)"
            echo "   Durée attendue: 10s"
            return 1
        else
            log_test "Transition Lobby→Nuit" "false" "Phase inattendue: $phase"
            echo "   Phase attendue: night"
            return 1
        fi
    else
        log_test "Transition Lobby→Nuit" "false" "Erreur état (HTTP $state_http_code)"
        return 1
    fi
}

# Test 6: Vérifier la stabilité du flux de jeu
test_game_flow_stability() {
    echo "🔍 Test 6: Vérification stabilité du flux de jeu..."
    
    if [ -z "$GAME_ID" ]; then
        log_test "Stabilité Flux" "false" "Pas de game_id disponible"
        return 1
    fi
    
    # Vérifier l'état 3 fois pour détecter des incohérences
    phases=()
    winners=()
    
    for i in {1..3}; do
        state_response=$(curl -s "$API_BASE/games/$GAME_ID/state" -w "HTTP_STATUS:%{http_code}")
        state_http_code=$(echo "$state_response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
        state_body=$(echo "$state_response" | sed 's/HTTP_STATUS:[0-9]*$//')
        
        if [ "$state_http_code" = "200" ]; then
            phase=$(echo "$state_body" | grep -o '"phase":"[^"]*"' | cut -d'"' -f4)
            winner=$(echo "$state_body" | grep -o '"winner":"[^"]*"' | cut -d'"' -f4)
            
            phases+=("$phase")
            if [ -n "$winner" ] && [ "$winner" != "null" ]; then
                winners+=("$winner")
            fi
        fi
        
        sleep 2
    done
    
    # Analyser les résultats
    if [ ${#winners[@]} -gt 0 ]; then
        log_test "Stabilité Flux" "false" "🚨 Victoire inattendue détectée: ${winners[0]}"
        echo "   États analysés: 3, Victoires: ${#winners[@]}"
        return 1
    fi
    
    # Vérifier la cohérence des phases (maximum 2 phases différentes = 1 transition)
    unique_phases=($(printf '%s\n' "${phases[@]}" | sort -u))
    
    if [ ${#unique_phases[@]} -le 2 ]; then
        log_test "Stabilité Flux" "true" "Flux de jeu stable"
        echo "   Phases observées: ${phases[*]}, Pas de victoire: ✓"
        return 0
    else
        log_test "Stabilité Flux" "false" "Phases instables: ${phases[*]}"
        return 1
    fi
}

# Fonction principale
main() {
    echo -e "${BLUE}🧪 DÉBUT DES TESTS DE VALIDATION DES CORRECTIONS${NC}"
    echo "============================================================"
    
    # Liste des tests
    tests=(
        "test_server_connection"
        "test_game_creation" 
        "test_add_players"
        "test_game_start_lobby_phase"
        "test_lobby_to_night_transition"
        "test_game_flow_stability"
    )
    
    passed=0
    total=${#tests[@]}
    
    # Exécuter chaque test
    for test_func in "${tests[@]}"; do
        if $test_func; then
            ((passed++))
        fi
        echo
    done
    
    # Résumé final
    echo "============================================================"
    echo -e "${BLUE}🎯 RÉSULTATS FINAUX: $passed/$total tests réussis${NC}"
    
    if [ $passed -eq $total ]; then
        echo -e "${GREEN}✅ TOUS LES TESTS SONT PASSÉS - CORRECTIONS VALIDÉES !${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  CERTAINS TESTS ONT ÉCHOUÉ - RÉVISION NÉCESSAIRE${NC}"
        return 1
    fi
}

# Lancer les tests
main