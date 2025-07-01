# 🌙 PROJET MIDNIGHT PACT - ROADMAP COMPLÈTE
## Transformation en Mafia SC2 Complet

---

# 👥 ÉQUIPE DE DÉVELOPPEMENT

## 🎯 **CHEF DE PROJET** - *Sarah Chen*
- **Responsabilités** : Planification, suivi des tâches, coordination équipe
- **Outils** : Roadmap, sprints, tests d'intégration
- **Objectif** : Livrer un jeu Mafia complet et cohérent

## 💻 **DÉVELOPPEUR PRINCIPAL** - *Alexandre Martin*
- **Responsabilités** : Backend, moteur de jeu, logique des rôles
- **Technologies** : Python/Flask, SQLAlchemy, WebSockets
- **Objectif** : Implémenter toutes les mécaniques de Mafia SC2

## 🎨 **UX/UI DESIGNER** - *Emma Rodriguez*
- **Responsabilités** : Interface utilisateur, expérience cohérente
- **Technologies** : React, shadcn/ui, design system
- **Objectif** : Interface intuitive pour 45+ rôles différents

## ✨ **ANIMATEUR/VFX** - *Thomas Wagner*
- **Responsabilités** : Animations, transitions, feedback visuel
- **Technologies** : CSS animations, Framer Motion, WebGL
- **Objectif** : Expérience immersive et dynamique

---

# 📋 SOMMAIRE GLOBAL - FONCTIONNALITÉS MANQUANTES

## 🏗️ **INFRASTRUCTURE DE BASE** 
- [ ] Système de procès/trial complet
- [ ] Chat nocturne entre factions
- [ ] Messages privés (PM)
- [ ] Système de testament (Last Will)
- [ ] Notes de mort (Death Notes)
- [ ] Ordre des actions nocturnes précis (11 étapes)

## 👥 **RÔLES TOWN** (20 manquants sur 22 total)
- [ ] **Investigatifs** : Sheriff, Investigator, Detective, Lookout, Coroner
- [ ] **Protectifs** : Bodyguard, Bus Driver, Escort  
- [ ] **Tueurs** : Vigilante, Veteran, Jailor
- [ ] **Gouvernement** : Mayor, Marshall, Mason, Mason Leader, Crier
- [ ] **Pouvoir** : Spy
- [ ] **Support** : Citizen (amélioré), autres spécialisés

## 🔴 **RÔLES MAFIA** (10 manquants sur 10 total)
- [ ] **Leadership** : Godfather, Mafioso
- [ ] **Déception** : Framer, Disguiser, Janitor
- [ ] **Support** : Consigliere, Consort, Blackmailer, Agent, Beguiler

## 🔵 **RÔLES TRIAD** (11 nouveaux)
- [ ] **Tueurs** : Dragon Head, Enforcer
- [ ] **Déception** : Deceiver, Forger, Incense Master
- [ ] **Support** : Administrator, Informant, Interrogator, Liaison, Silencer, Vanguard

## ⚪ **RÔLES NEUTRES** (15 manquants sur 15 total)
- [ ] **Tueurs** : Serial Killer, Arsonist, Mass Murderer
- [ ] **Maléfiques** : Jester, Executioner, Witch, Witch Doctor, Cultist
- [ ] **Bénins** : Survivor, Amnesiac, Judge, Auditor, Electromaniac

## ⚙️ **SYSTÈMES AVANCÉS**
- [ ] Options d'hôte (Day Type, Night Type, Trial Settings)
- [ ] Système de points et déblocables
- [ ] Mode spectateur pour les morts
- [ ] Variants de jeu (Classic, Clue, Custom)
- [ ] Achievments/succès

---

# 🗺️ ROADMAP PAR CHAPITRES

## 📖 **CHAPITRE 1 : FONDATIONS SOLIDES** (4 semaines)
*Corriger le système actuel pour qu'il soit conforme à Mafia SC2*

### 🎯 **Sprint 1.1 : Système de Vote/Procès** (1 semaine)
**🎯 Chef de Projet :**
- [ ] Analyser les 4 types de vote de SC2
- [ ] Définir les specs du système de procès
- [ ] Planifier les phases DISCUSSION → VOTE → TRIAL → LYNCH

**💻 Développeur :**
- [ ] Créer enum Phase avec TRIAL, LYNCHING
- [ ] Implémenter logique de vote majoritaire vs ballot
- [ ] Système de défense et vote innocent/coupable
- [ ] Timer séparé pour chaque phase

**🎨 UX Designer :**
- [ ] Mockups interface de procès
- [ ] Panel de défense pour l'accusé
- [ ] Interface de vote innocent/coupable
- [ ] Indicateurs visuels des phases

**✨ Animateur :**
- [ ] Animation de transition vers le procès
- [ ] Effet spotlight sur l'accusé
- [ ] Animation de verdict et exécution
- [ ] Sons d'ambiance tribunal

**🐛 Bugs Potentiels :**
- Synchronisation des timers entre clients
- Gestion des déconnexions pendant procès
- Race conditions sur les votes simultanés

### 🎯 **Sprint 1.2 : Ordre Actions Nocturnes** (1 semaine)
**💻 Développeur :**
- [ ] Implémenter l'ordre SC2 à 11 étapes
- [ ] Gérer les actions simultanées vs séquentielles
- [ ] Système de priorité pour résoudre les conflits

**🐛 Bugs Potentiels :**
- Actions interdépendantes (Bus Driver + autres)
- Paradoxes temporels (A protège B qui tue A)
- Rollback d'actions invalides

### 🎯 **Sprint 1.3 : Messages et Communication** (1 semaine)
**💻 Développeur :**
- [ ] Système PM avec notification publique
- [ ] Chat nocturne par faction
- [ ] Système de testament (Last Will)
- [ ] Notes de mort des tueurs

**🎨 UX Designer :**
- [ ] Interface PM intuitive
- [ ] Chat nocturne sécurisé par faction
- [ ] Éditeur de testament
- [ ] Affichage des notes de mort

### 🎯 **Sprint 1.4 : Tests et Debug** (1 semaine)
**👥 Toute l'équipe :**
- [ ] Tests d'intégration complets
- [ ] Simulation de parties complètes
- [ ] Correction des bugs critiques
- [ ] Optimisation performances

---

## 📖 **CHAPITRE 2 : RÔLES INVESTIGATIFS** (3 semaines)
*Ajouter tous les rôles d'investigation pour donner de l'information au Town*

### 🎯 **Sprint 2.1 : Sheriff & Investigator** (1 semaine)
**💻 Développeur :**
- [ ] **Sheriff** : Détecte "Suspect" vs "Not Suspicious"
- [ ] **Investigator** : Donne indices sur type de rôle
- [ ] Système de résistance (Godfather immunisé)
- [ ] Messages d'investigation clairs

**🎨 UX Designer :**
- [ ] Interface d'investigation nocturne
- [ ] Affichage des résultats avec icônes
- [ ] Historique des investigations
- [ ] Codes couleur Suspect/Innocent

**✨ Animateur :**
- [ ] Animation d'investigation (loupe, radar)
- [ ] Effet de révélation du résultat
- [ ] Particules pour succès/échec
- [ ] Sons d'investigation mystérieux

### 🎯 **Sprint 2.2 : Detective & Lookout** (1 semaine)
**💻 Développeur :**
- [ ] **Detective** : Investigue morts pour plus d'infos
- [ ] **Lookout** : Voit qui visite la cible
- [ ] **Coroner** : Révèle rôle exact des morts nettoyés

**🎨 UX Designer :**
- [ ] Interface spécialisée par rôle
- [ ] Rapport de surveillance Lookout
- [ ] Autopsy report du Coroner
- [ ] Timeline des visites Detective

### 🎯 **Sprint 2.3 : Spy & Tests** (1 semaine)
**💻 Développeur :**
- [ ] **Spy** : Écoute chat Mafia, voit leurs cibles
- [ ] Intégration avec chat nocturne sécurisé
- [ ] Système de logs pour investigations

**🐛 Bugs Potentiels :**
- Investigations sur cibles qui changent (Bus Driver)
- Spy voyant infos après changement de faction
- Révélations incohérentes entre rôles

---

## 📖 **CHAPITRE 3 : RÔLES MAFIA** (3 semaines)
*Créer la faction Mafia complète avec hiérarchie et pouvoirs*

### 🎯 **Sprint 3.1 : Leadership Mafia** (1 semaine)
**💻 Développeur :**
- [ ] **Godfather** : Leader, immunisé Sheriff, peut tuer
- [ ] **Mafioso** : Exécute ordres, devient GF si mort
- [ ] Chat nocturne Mafia avec hiérarchie
- [ ] Système de succession automatique

### 🎯 **Sprint 3.2 : Déception Mafia** (1 semaine)
**💻 Développeur :**
- [ ] **Framer** : Fait apparaître innocent comme suspect
- [ ] **Janitor** : Cache rôle des morts
- [ ] **Disguiser** : Prend identité de sa victime
- [ ] Interaction avec investigations Town

### 🎯 **Sprint 3.3 : Support Mafia** (1 semaine)
**💻 Développeur :**
- [ ] **Consigliere** : Investigation pour Mafia
- [ ] **Consort** : Bloque actions nocturnes
- [ ] **Blackmailer** : Empêche de parler le jour
- [ ] **Agent/Beguiler** : Rôles support avancés

---

## 📖 **CHAPITRE 4 : RÔLES TOWN AVANCÉS** (4 semaines)
*Compléter tous les rôles Town pour équilibrer le jeu*

### 🎯 **Sprint 4.1 : Protectifs Avancés** (1 semaine)
**💻 Développeur :**
- [ ] **Bodyguard** : Tue attaquant en se sacrifiant
- [ ] **Bus Driver** : Échange positions de 2 joueurs
- [ ] **Escort** : Bloque actions nocturnes (Town)
- [ ] Interactions complexes entre protections

### 🎯 **Sprint 4.2 : Tueurs Town** (1 semaine)
**💻 Développeur :**
- [ ] **Vigilante** : Peut tuer la nuit (limité)
- [ ] **Veteran** : Tue tous les visiteurs
- [ ] **Jailor** : Emprisonne et peut exécuter
- [ ] Système d'auto-sanctions (Vigi tue innocent)

### 🎯 **Sprint 4.3 : Gouvernement** (1 semaine)
**💻 Développeur :**
- [ ] **Mayor** : Vote double, peut se révéler
- [ ] **Marshall** : Alternative au Mayor
- [ ] **Mason/Mason Leader** : Équipe confirmée
- [ ] **Crier** : Announcements publics

### 🎯 **Sprint 4.4 : Citizen Amélioré** (1 semaine)
**💻 Développeur :**
- [ ] Citizen avec testament amélioré
- [ ] Possibilité de promotion en Mason
- [ ] Rôle de backup pour autres morts

---

## 📖 **CHAPITRE 5 : FACTION TRIAD** (3 semaines)
*Nouvelle faction complète pour complexifier le jeu*

### 🎯 **Sprint 5.1 : Leadership Triad** (1 semaine)
**💻 Développeur :**
- [ ] **Dragon Head** : Leader Triad
- [ ] **Enforcer** : Tueur principal
- [ ] Chat nocturne Triad séparé
- [ ] Mécaniques faction indépendante

### 🎯 **Sprint 5.2 : Déception Triad** (1 semaine)
**💻 Développeur :**
- [ ] **Deceiver** : Manipule investigations
- [ ] **Forger** : Falsifie testaments
- [ ] **Incense Master** : Cache morts

### 🎯 **Sprint 5.3 : Support Triad** (1 semaine)
**💻 Développeur :**
- [ ] **Administrator, Informant, Interrogator**
- [ ] **Liaison, Silencer, Vanguard**
- [ ] Pouvoirs uniques Triad vs Mafia

---

## 📖 **CHAPITRE 6 : RÔLES NEUTRES** (4 semaines)
*Rôles indépendants qui changent complètement la dynamique*

### 🎯 **Sprint 6.1 : Neutres Tueurs** (1 semaine)
**💻 Développeur :**
- [ ] **Serial Killer** : Tue chaque nuit, immunisé détection
- [ ] **Arsonist** : Douse puis incinère multiple
- [ ] **Mass Murderer** : Massacre avec tronçonneuse
- [ ] Conditions victoire indépendantes

### 🎯 **Sprint 6.2 : Neutres Chaos** (1 semaine)
**💻 Développeur :**
- [ ] **Jester** : Gagne si lynché, tue qui vote
- [ ] **Executioner** : Doit faire lyncher cible
- [ ] **Witch** : Contrôle actions autres joueurs
- [ ] Mécaniques de manipulation

### 🎯 **Sprint 6.3 : Neutres Support** (1 semaine)
**💻 Développeur :**
- [ ] **Survivor** : Juste survivre
- [ ] **Amnesiac** : Devient rôle d'un mort
- [ ] **Judge** : Pouvoirs de jugement
- [ ] **Auditor** : Contrôle administratif

### 🎯 **Sprint 6.4 : Culte System** (1 semaine)
**💻 Développeur :**
- [ ] **Cultist** : Recrute nouvelles conversion
- [ ] **Witch Doctor** : Soigne et convertit
- [ ] Chat nocturne Culte
- [ ] Système de conversion complet

---

## 📖 **CHAPITRE 7 : SYSTÈMES AVANCÉS** (3 semaines)
*Options d'hôte et fonctionnalités professionnelles*

### 🎯 **Sprint 7.1 : Options Host** (1 semaine)
**💻 Développeur :**
- [ ] **Day Types** : Majority, Ballot, +Trial variants
- [ ] **Night Types** : Classic, Death Descriptions, Sequence
- [ ] **Trial Settings** : Temps, défense, pause
- [ ] **Misc** : Durées, testament on/off, PM on/off

### 🎯 **Sprint 7.2 : Système Points** (1 semaine)
**💻 Développeur :**
- [ ] Points par performance (win/lose/survie)
- [ ] Déblocables : modèles, accessoires
- [ ] Blacklist/prefer roles
- [ ] Statistiques joueur

### 🎯 **Sprint 7.3 : Modes de Jeu** (1 semaine)
**💻 Développeur :**
- [ ] **Classic** : Rôles de base seulement
- [ ] **Clue** : Pas de révélation rôle
- [ ] **Custom/Save Slot** : Setups sauvegardés
- [ ] Achievements système

---

## 📖 **CHAPITRE 8 : POLISH & RELEASE** (3 semaines)
*Finalisation pour expérience AAA*

### 🎯 **Sprint 8.1 : Interface Finale** (1 semaine)
**🎨 UX Designer :**
- [ ] Révision complète UX/UI
- [ ] Guide intégré pour 45+ rôles
- [ ] Tooltips et aide contextuelle
- [ ] Thèmes visuels par faction

### 🎯 **Sprint 8.2 : Animations Maîtrisées** (1 semaine)
**✨ Animateur :**
- [ ] Animations uniques par rôle
- [ ] Transitions fluides entre phases
- [ ] Effets de mort variés
- [ ] Ambiance sonore immersive

### 🎯 **Sprint 8.3 : Tests Finaux** (1 semaine)
**👥 Toute l'équipe :**
- [ ] Tests de charge (15 joueurs simultanés)
- [ ] Tests d'équilibrage avec tous rôles
- [ ] Optimisation performances
- [ ] Documentation complète

---

# 📊 SUIVI DE PROJET

## 🎯 **MÉTRIQUES DE SUCCÈS**
- **Rôles implémentés** : 0/45+ (Target: 100%)
- **Systèmes complets** : 0/8 (Phases, Chat, PM, Testament, etc.)
- **Performance** : <100ms latence, 60fps constant
- **Bugs critiques** : 0 en production

## ⏱️ **PLANNING GLOBAL**
- **Durée totale** : 28 semaines (~7 mois)
- **Livrable Alpha** : Fin Chapitre 4 (18 semaines)
- **Livrable Beta** : Fin Chapitre 7 (25 semaines)
- **Release 1.0** : Fin Chapitre 8 (28 semaines)

## 🔄 **PROCESS DE DÉVELOPPEMENT**
1. **Spec** : Chef de projet définit requirements
2. **Dev** : Développeur implémente backend + API
3. **UI** : Designer crée interface utilisateur
4. **Animation** : Animateur ajoute polish visuel
5. **Test** : Équipe teste et debug
6. **Review** : Validation qualité avant next sprint

## 🚨 **RISQUES IDENTIFIÉS**
- **Complexité** : 45+ rôles = interactions exponentielles
- **Performance** : Temps réel avec 15 joueurs
- **Équilibrage** : Chaque rôle doit être fun et viable
- **Scope Creep** : Fonctionnalités supplémentaires

## 🎉 **OBJECTIF FINAL**
Créer le **Mafia en ligne le plus complet et moderne**, surpassant même SC2 Mafia en expérience utilisateur, avec interface moderne, animations fluides, et toutes les mécaniques avancées pour une expérience multijoueur parfaite !

---

*Dernière mise à jour : Phase de Planification*  
*Prochaine révision : Fin Sprint 1.1*