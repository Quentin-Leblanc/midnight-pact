# Analyse du Projet Midnight Pact - Jeu Loup-Garou/Mafia

## Vue d'ensemble du projet actuel

Votre projet "Midnight Pact" est un jeu de type loup-garou avec une architecture moderne comprenant :

### Backend (Python/Flask)
- **Moteur de jeu** : `game_engine.py` - gestion complète des phases et mécaniques
- **Modèles de données** : SQLAlchemy pour la persistance
- **API REST** : Routes pour toutes les actions de jeu
- **Phases implémentées** : Nuit, Jour, Vote, Transition, Événements

### Frontend (React/Vite)
- **Interface moderne** : Utilisation de shadcn/ui pour les composants
- **Chat en temps réel** : Système de messagerie intégré
- **Animations** : Transitions entre phases avec effets visuels
- **Responsive** : Interface adaptable avec thème sombre

### Rôles actuellement implémentés
- **Village** : Villageois, Voyant, Sorcière, Garde, Chasseur
- **Loups-garous** : Loup-garou standard
- **Mécaniques de base** : Actions nocturnes, votes, éliminations

## Différences principales avec Mafia SC2

### 1. **Système de phases de jour/vote**

**Mafia SC2** utilise un système complexe :
- **Day Cycle** : Discussion libre
- **Lynch Cycle** : Vote puis procès optionnel
- **Trial System** : Le joueur peut se défendre avant l'exécution finale
- **Types de vote** : Majorité, Majorité+Procès, Scrutin secret, Scrutin+Procès

**Votre système actuel** :
- Phase jour combinée avec vote direct
- Pas de système de procès/défense
- Vote majoritaire simple

### 2. **Ordre des actions nocturnes**

**Mafia SC2** a un ordre très précis (11 étapes) :
1. Geôlier/Kidnappeur détient la cible
2. Discussion nocturne des factions
3. Gilets pare-balles utilisés
4. Changements de cible et blocages de rôles
5. Framer, Incendiaire, actions diverses
6. **Tous les rôles tueurs agissent simultanément**
7. Nettoyeur nettoie
8. **Rôles d'investigation détectent**
9. Déguisement remplace la cible
10. Leader Mason recrute
11. Culte recrute

**Votre système actuel** :
- Ordre simplifié : Protection → Attaques → Guérison/Poison → Investigation
- Moins de complexité dans les interactions

### 3. **Rôles manquants importants de Mafia SC2**

#### Ville (Town)
- **Sheriff** : Détecte si quelqu'un est suspect (Mafia/Neutre maléfique)
- **Investigator** : Obtient des indices sur le type de rôle
- **Jailor** : Peut emprisonner et exécuter
- **Mayor** : Vote compte double, peut se révéler
- **Bodyguard** : Protège en tuant l'attaquant
- **Spy** : Écoute les conversations de la Mafia

#### Mafia
- **Godfather** : Immunisé aux détections du Sheriff
- **Mafioso** : Exécute les ordres du Parrain
- **Consigliere** : Investigation pour la Mafia
- **Janitor** : Cache le rôle des morts
- **Framer** : Fait apparaître innocents comme suspects

#### Neutres
- **Serial Killer** : Tue chaque nuit, gagne seul
- **Arsonist** : Asperge puis brûle plusieurs personnes
- **Jester** : Gagne s'il est lynché
- **Executioner** : Doit faire lyncher une cible spécifique
- **Survivor** : Doit juste survivre jusqu'à la fin

### 4. **Mécaniques avancées manquantes**

- **Système de testament** : Message laissé après la mort
- **Messages privés** : Communication secrète entre joueurs
- **Notes de mort** : Messages des tueurs
- **Système de points** : Récompenses et progression
- **Multiple factions** : Triades, Cultes, etc.

## Recommandations d'amélioration

### Phase 1 : Correction du système de vote/procès

1. **Séparer les phases jour et vote**
   ```python
   class Phase(Enum):
       WAITING = "waiting"
       NIGHT = "night"
       DAY = "day"           # Discussion libre
       VOTING = "voting"     # Vote pour désigner un suspect
       TRIAL = "trial"       # Procès du suspect
       LYNCHING = "lynching" # Exécution
       TRANSITION = "events"
       ENDED = "ended"
   ```

2. **Implémenter le système de procès**
   - Temps de défense pour l'accusé
   - Vote innocent/coupable séparé
   - Possibilité de gracier

### Phase 2 : Enrichissement des rôles

1. **Ajouter les rôles investigatifs**
   ```python
   class Role(Enum):
       # Existants
       VILLAGER = "villager"
       WEREWOLF = "werewolf" 
       SEER = "seer"
       WITCH = "witch"
       GUARD = "bodyguard"
       HUNTER = "hunter"
       
       # Nouveaux - Investigation
       SHERIFF = "sheriff"      # Détecte suspects
       INVESTIGATOR = "investigator"  # Obtient indices
       SPY = "spy"             # Écoute Mafia
       
       # Nouveaux - Mafia
       GODFATHER = "godfather"   # Leader invisible
       MAFIOSO = "mafioso"      # Exécutant
       CONSIGLIERE = "consigliere"  # Investigateur Mafia
       JANITOR = "janitor"      # Cache rôles
       
       # Nouveaux - Neutres
       SERIAL_KILLER = "serial_killer"
       JESTER = "jester"
       EXECUTIONER = "executioner"
       SURVIVOR = "survivor"
   ```

2. **Corriger l'ordre des actions nocturnes**
   ```python
   def _process_night_actions(self, game):
       # 1. Détentions (Jailor)
       # 2. Protections et blocages
       # 3. Actions spéciales (Framer, etc.)
       # 4. TOUS les kills simultanément
       # 5. Nettoyage (Janitor)
       # 6. Investigations
       # 7. Recrutements
   ```

### Phase 3 : Mécaniques avancées

1. **Système de testament et messages**
   - Dernière volonté affichée à la mort
   - Messages privés entre joueurs
   - Notes de mort des tueurs

2. **Interface améliorée**
   - Panel de procès avec timer
   - Historique des votes visibles
   - Indicateurs de statut des rôles

3. **Animations et effets**
   - Animations spécifiques par type de mort
   - Effets visuels pour les pouvoirs
   - Sons d'ambiance selon les phases

## Structure de développement recommandée

```
midnight_pact/
├── werewolf_game_backend/
│   ├── src/
│   │   ├── game_engine.py          # ✅ Moteur principal (à améliorer)
│   │   ├── roles/                  # 🆕 Module pour chaque rôle
│   │   │   ├── base_role.py
│   │   │   ├── town_roles.py
│   │   │   ├── mafia_roles.py
│   │   │   └── neutral_roles.py
│   │   ├── mechanics/              # 🆕 Mécaniques de jeu
│   │   │   ├── voting_system.py
│   │   │   ├── trial_system.py
│   │   │   └── night_actions.py
│   │   └── utils/                  # 🆕 Utilitaires
│   │       ├── phase_manager.py
│   │       └── game_balance.py
└── werewolf_game_frontend/
    └── src/
        ├── components/
        │   ├── game/               # 🆕 Composants de jeu
        │   │   ├── TrialPanel.jsx
        │   │   ├── VotingPanel.jsx
        │   │   └── RolePanel.jsx
        │   └── animations/         # 🆕 Animations spécialisées
        └── hooks/                  # 🆕 Hooks React personnalisés
            └── useGamePhases.js
```

## Priorités de développement

### Priorité 1 (Urgent)
1. **Corriger le système de vote/procès** selon Mafia SC2
2. **Ajouter les rôles investigatifs de base** (Sheriff, Investigator)
3. **Améliorer l'ordre des actions nocturnes**

### Priorité 2 (Important)
1. **Implémenter les rôles Mafia avancés** (Godfather, Janitor)
2. **Ajouter le système de testament**
3. **Créer les rôles neutres** (Serial Killer, Jester)

### Priorité 3 (Améliorations)
1. **Interface de procès avancée**
2. **Système de points et progression**
3. **Animations et effets spéciaux**
4. **Mode spectateur pour les morts**

## Conclusion

Votre projet a une excellente base technique et une interface moderne. Les principales améliorations concernent :

1. **Fidélité aux mécaniques de Mafia SC2** - Le système de vote/procès est crucial
2. **Richesse des rôles** - Plus de rôles = plus de stratégies possibles  
3. **Équilibrage** - L'ordre des actions nocturnes affecte profondément l'équilibre
4. **Expérience utilisateur** - Interface intuitive pour les mécaniques complexes

Le mélange entre l'esprit loup-garou traditionnel et les mécaniques avancées de Mafia SC2 peut créer une expérience unique et captivante !