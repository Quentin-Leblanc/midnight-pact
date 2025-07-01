# Analyse du Projet Loup-Garou / Mafia SC2 - "Midnight Pact"

## 📋 État Actuel du Projet

### Architecture Existante
- **Backend** : Flask + SocketIO + SQLAlchemy (Python)
- **Frontend** : React + Vite + TailwindCSS + shadcn/ui
- **Base de données** : SQLite
- **Communication** : REST API + WebSockets

### Fonctionnalités Actuellement Implémentées ✅
- Système de lobby avec création/rejoindre des parties
- 6 rôles de base : Loup-Garou, Voyant, Sorcière, Garde, Chasseur, Villageois
- Phases Nuit/Jour basiques avec timer
- Système de vote simple
- Chat en temps réel
- Interface responsive avec animations

## 🎯 Analyse des Mécaniques SC2 Mafia vs Implémentation Actuelle

### Différences Clés Identifiées

#### 1. **Système de Phases** 🔄
**SC2 Mafia :**
- 3 phases distinctes : Day Cycle → Lynch Cycle → Night Cycle
- Lynch Cycle séparé avec système de "procès" (trial)
- Ordre strict des actions nocturnes avec priorités

**Votre implémentation actuelle :**
- 2 phases : Nuit → Jour (avec vote intégré)
- Pas de système de procès
- Actions nocturnes simultanées sans ordre de priorité

#### 2. **Système de Vote et Lynch** ⚖️
**SC2 Mafia :**
- Vote par majorité simple OU 51% selon le mode
- Phase de procès où l'accusé peut se défendre
- Vote guilty/innocent après la défense
- Variété de méthodes d'exécution (RP)

**Votre implémentation :**
- Vote direct pendant la journée
- Élimination immédiate sans procès

#### 3. **Rôles et Mécaniques** 👥
**SC2 Mafia (108+ rôles) :**
- **Town** : Bodyguard, Bus Driver, Jailor, Detective, Mayor, Marshall, etc.
- **Mafia** : Godfather, Consigliere, Janitor, Disguiser, Framer, etc.  
- **Neutral** : Serial Killer, Arsonist, Jester, Survivor, Witch, etc.
- **Triad** : Dragon Head, Administrator, Enforcer, etc.

**Votre implémentation (6 rôles) :**
- Rôles de base du loup-garou français

#### 4. **Ordre des Actions Nocturnes** 🌙
**SC2 Mafia - Ordre strict :**
1. Jailor/Kidnapper détient la cible
2. Communications nocturnes (Mafia, Mason, Cult)
3. Bulletproof vests utilisés
4. Redirections et roleblock (Witch, Bus Driver, Escort)
5. Framer, Arsonist, actions diverses
6. Actions de kill simultanées (avec priorités)
7. Janitor nettoie
8. Rôles d'investigation
9. Disguiser remplace sa cible
10. Recrutements (Mason Leader, Cult)

**Votre implémentation :**
- Actions traitées de manière basique sans ordre strict

## 🚀 Recommandations d'Amélioration

### Phase 1 : Correction des Mécaniques de Base

#### A. **Système de Phases Amélioré**
```python
class Phase(Enum):
    WAITING = "waiting"
    DAY = "day"           # Discussion libre
    VOTING = "voting"     # Vote pour désigner un suspect  
    TRIAL = "trial"       # Procès du suspect
    LYNCH = "lynch"       # Exécution ou acquittement
    NIGHT = "night"       # Actions nocturnes
    TRANSITION = "events" # Résultats de la nuit
```

#### B. **Ordre des Actions Nocturnes**
Implémenter un système de priorités :
1. **Détentions** (Jailor)
2. **Communications** (Mafia chat, Mason chat)
3. **Protections** (Bodyguard, Doctor)
4. **Redirections** (Bus Driver, Witch)
5. **Roleblock** (Escort/Consort)
6. **Investigations** (Sheriff, Detective)
7. **Kills** (Mafia, Serial Killer, Vigilante)
8. **Nettoyage** (Janitor)
9. **Déguisements** (Disguiser)

#### C. **Système de Procès**
```python
class TrialPhase:
    - suspect_defense_time: 30s  # Temps de défense
    - voting_time: 20s           # Vote guilty/innocent
    - required_votes: majority   # Votes nécessaires
    - execution_methods: ['lynch', 'shooting', 'poison', etc.]
```

### Phase 2 : Nouveaux Rôles Prioritaires

#### Rôles Town à Ajouter :
1. **Jailor** - Peut emprisonner et exécuter
2. **Detective** - Version améliorée du Voyant (rôle exact)
3. **Bodyguard** - Protège en se sacrifiant
4. **Mayor** - Révélable avec double vote
5. **Doctor** - Soigne les blessés
6. **Escort** - Roleblock

#### Rôles Mafia à Ajouter :
1. **Godfather** - Immune la nuit, apparaît innocent
2. **Consigliere** - Version Mafia du Detective  
3. **Janitor** - Nettoie les corps (cache le rôle)
4. **Disguiser** - Prend l'apparence de sa victime
5. **Framer** - Fait paraître innocent comme coupable
6. **Consort** - Roleblock Mafia

#### Rôles Neutral à Ajouter :
1. **Serial Killer** - Killer solo, gagne seul
2. **Arsonist** - Douse puis brûle plusieurs personnes
3. **Jester** - Gagne s'il est lynché
4. **Survivor** - Juste survivre
5. **Witch** - Contrôle les actions des autres

### Phase 3 : Interface et UX

#### A. **Interface SC2-Style**
- Boutons de vote individuels pour chaque joueur
- Zone de chat avec onglets (All, Mafia, Dead, etc.)
- Panel de rôle avec description détaillée
- Last Will system
- Death Note system

#### B. **Système de Commandes**
```
-vote [player]     # Vote contre un joueur
-unvote           # Retire son vote  
-guilty           # Vote guilty lors du procès
-innocent         # Vote innocent lors du procès
-pm [player] [msg] # Message privé
-will [text]      # Testament
-target [player]  # Suggestion de cible (Mafia)
```

#### C. **Animations et Effets**
- Animations de transition entre phases
- Effets visuels pour les morts
- Sons d'ambiance selon la phase
- Particles effects pour les actions spéciales

### Phase 4 : Système Avancé

#### A. **Modes de Jeu**
1. **Classic** - Setup équilibré standard
2. **Chaos** - Beaucoup de rôles neutres
3. **Mafia Power** - Mafia renforcée
4. **Investigative** - Beaucoup de rôles d'enquête

#### B. **Système de Points et Rang**
- Points gagnés selon performance
- Unlockables (avatars, couleurs, titres)
- Système de rang/niveau
- Statistiques détaillées

#### C. **Fonctionnalités Sociales**
- Amis et blacklist
- Spectateur mode
- Replay des parties
- Matchmaking par niveau

## 🛠️ Plan d'Implémentation Technique

### Priorité 1 : Moteur de Jeu ⚡
1. Refactorer `game_engine.py` pour les nouvelles phases
2. Implémenter l'ordre des actions nocturnes
3. Système de procès et vote
4. Gestion des priorités d'actions

### Priorité 2 : Nouveaux Rôles 👥  
1. Créer système modulaire de rôles
2. Implémenter 5-10 rôles prioritaires
3. Tests et équilibrage
4. Documentation des rôles

### Priorité 3 : Interface ✨
1. Refonte du GameRoom.jsx
2. Nouveau système de vote
3. Chat amélioré avec onglets
4. Animations et transitions

### Priorité 4 : Features Avancées 🚀
1. Modes de jeu multiples
2. Système de points
3. Matchmaking
4. Spectateur mode

## 🎨 Styling et Thème

### Direction Artistique
- **Palette** : Garder le thème sombre actuel mais avec des accents colorés par faction
- **Town** : Bleu/Blanc (justice, ordre)
- **Mafia** : Rouge/Noir (danger, mystère)  
- **Neutral** : Violet/Orange (chaos, imprévisibilité)
- **Animations** : Plus fluides, inspirées de SC2
- **SFX** : Sons atmosphériques selon les phases

## 📊 Métriques de Succès

### Objectifs Court Terme (1-2 mois)
- [ ] Système de procès fonctionnel
- [ ] 10 rôles supplémentaires implémentés
- [ ] Ordre des actions nocturnes correct
- [ ] Interface améliorée

### Objectifs Moyen Terme (3-6 mois)  
- [ ] 25+ rôles disponibles
- [ ] Système de points et progression
- [ ] Multiples modes de jeu
- [ ] Base de joueurs stable (50+ joueurs réguliers)

### Objectifs Long Terme (6-12 mois)
- [ ] Tournois et événements
- [ ] Système de clan/guilde
- [ ] Mobile responsive parfait
- [ ] Communauté active avec forum

## 🔧 Outils et Ressources

### Documentation Technique
- [SC2 Mafia Wiki](https://sc2mafia.fandom.com) - Référence complète
- [Mafia Scum](https://wiki.mafiascum.net) - Wiki communautaire
- [Town of Salem](https://www.blankmediagames.com/) - Inspiration interface

### Assets Recommandés
- Icônes Lucide (déjà utilisé) + FontAwesome
- Sounds : Zapsplat, Freesound
- Animations : Framer Motion (déjà compatible React)
- Fonts : Inter (moderne) + Cinzel (médiéval pour le thème)

---

## 💡 Conclusion

Votre projet a une excellente base technique. Les principales améliorations pour se rapprocher de SC2 Mafia sont :

1. **Système de phases plus complexe** avec procès
2. **Beaucoup plus de rôles** (minimum 20-25)
3. **Ordre strict des actions** nocturnes  
4. **Interface plus sophistiquée** avec boutons de vote individuels
5. **Mécaniques avancées** (Last Will, Death Notes, etc.)

L'objectif est de transformer votre loup-garou en ligne en véritable **SC2 Mafia experience** tout en gardant l'esprit français du jeu original.

**Recommandation immédiate** : Commencer par le système de procès et ajouter 5 rôles prioritaires (Godfather, Detective, Jailor, Serial Killer, Jester) pour avoir une base solide.