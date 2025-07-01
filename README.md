# Loup-Garou Online - Documentation Finale

## 🎯 Objectif Accompli
Création d'un jeu de Loup-Garou en ligne multijoueur avec système de lobby inspiré de SC2 Mafia.

## 🏗️ Architecture

### Backend (Flask)
- **Framework** : Flask + Flask-SocketIO + SQLAlchemy
- **Base de données** : SQLite
- **API REST** : Gestion des parties, joueurs, et actions de jeu
- **WebSockets** : Communication temps réel
- **Port** : 5000

### Frontend (React)
- **Framework** : React + Vite
- **UI** : TailwindCSS + shadcn/ui
- **État** : React Hooks
- **Communication** : Fetch API + WebSockets
- **Port** : 5173

## 🎮 Fonctionnalités

### Lobby
- Création de parties avec nom et limite de joueurs
- Rejoindre par code de salle
- Liste des parties disponibles
- Interface inspirée de SC2 Mafia

### Jeu
- **Rôles** : Loup-Garou, Voyant, Sorcière, Garde, Chasseur, Villageois
- **Phases** : Nuit (actions), Jour (discussion), Vote (élimination)
- **Actions spéciales** par rôle
- **Conditions de victoire** automatiques

## 🚀 Démarrage

### Backend
```bash
cd werewolf_game_backend
source venv/bin/activate
python src/main.py
```

### Frontend
```bash
cd werewolf_game_frontend
pnpm run dev
```

## 📁 Structure des Fichiers

```
werewolf_game/
├── werewolf_game_backend/
│   ├── src/
│   │   ├── main.py              # Application Flask principale
│   │   ├── game_engine.py       # Moteur de jeu
│   │   ├── models/
│   │   │   └── game.py          # Modèles de base de données
│   │   └── routes/
│   │       ├── game.py          # Routes de gestion des parties
│   │       └── gameplay.py      # Routes de gameplay
│   └── venv/                    # Environnement virtuel Python
└── werewolf_game_frontend/
    ├── src/
    │   ├── App.jsx              # Composant principal (lobby)
    │   └── GameRoom.jsx         # Interface de jeu
    └── package.json             # Dépendances Node.js
```

## 🎯 Fonctionnalités Testées

### ✅ Backend
- Création de parties
- Ajout de joueurs
- Démarrage de jeu
- Attribution des rôles
- État du jeu

### ✅ Frontend
- Navigation lobby/jeu
- Formulaires de création/rejoindre
- Interface de jeu responsive
- Affichage des rôles et phases

## 🔧 API Endpoints

### Parties
- `GET /api/games` - Liste des parties
- `POST /api/games` - Créer une partie
- `POST /api/games/{code}/join` - Rejoindre une partie

### Gameplay
- `POST /api/games/{code}/start` - Démarrer le jeu
- `GET /api/games/{code}/state` - État du jeu
- `GET /api/games/{code}/player/{name}/role` - Rôle du joueur
- `POST /api/games/{code}/night-action` - Action nocturne
- `POST /api/games/{code}/vote` - Vote d'élimination

## 🎨 Design
- **Thème** : Sombre avec dégradés bleu/ardoise
- **Inspiration** : Interface SC2 Mafia
- **Responsive** : Compatible mobile et desktop
- **Icônes** : Lucide React
- **Animations** : Transitions CSS fluides

## 🚀 Prêt pour Déploiement
Le jeu est entièrement fonctionnel et prêt à être déployé en production avec les outils de déploiement disponibles.

---
*Développé avec succès selon les spécifications demandées*

