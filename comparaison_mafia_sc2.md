# 🎯 **COMPARAISON MIDNIGHT PACT vs MAFIA SC2**

## 📊 **ÉTAT ACTUEL DU DÉVELOPPEMENT**

### ✅ **FONCTIONNALITÉS IMPLEMENTÉES**
1. **Système de procès complet** ✓
   - Vote → Procès → Verdict → Exécution/libération
   - 4 types de vote (Majority, Majority+Trial, Ballot, Ballot+Trial)
   - Interface dramatique avec animations

2. **Chat simple** ✓
   - Chat public pendant le jour
   - Messages du système
   - Chat transparent amélioré

3. **Testament & Notes de mort** ✓
   - Testaments révélés à la mort
   - Notes de mort des tueurs
   - Interface dédiée

4. **Rôles investigatifs** ✓
   - Sheriff : Investigation suspect/non-suspect
   - Investigator : Analyse par groupes de rôles
   - Interface panneau d'investigation

5. **Système de phases avec animations** ✓
   - Affichage style Mafia SC2
   - Transitions animées entre phases
   - Couleurs et effets spécifiques par phase

---

## ❌ **FONCTIONNALITÉS MANQUANTES CRITIQUES**

### 1. **SYSTÈME DE RÔLES ÉTENDU** (Priorité: CRITIQUE)
#### **État actuel:** 8 rôles seulement
- Villageois, Loup-garou, Voyant, Sorcière, Garde, Chasseur, Sheriff, Investigator

#### **Objectif Mafia SC2:** 45+ rôles répartis en factions
- **TOWN (Village):** 20+ rôles
  - Random Town, Bodyguard, Doctor, Escort, Investigator, Jailor, Lookout, Mayor, Medium, Psychic, Retributionist, Sheriff, Spy, Transporter, Vampire Hunter, Veteran, Vigilante
- **MAFIA:** 10+ rôles  
  - Godfather, Mafioso, Blackmailer, Consigliere, Consort, Disguiser, Forger, Framer, Janitor, Hypnotist
- **NEUTRAL:** 15+ rôles
  - Amnesiac, Arsonist, Executioner, Jester, Juggernaut, Plaguebearer, Serial Killer, Survivor, Vampire, Werewolf, Witch

### 2. **SYSTÈME DE FACTIONS** (Priorité: CRITIQUE)
#### **État actuel:** 2 factions (Village vs Loups-garous)
#### **Objectif Mafia SC2:** 4 factions principales
- **Town** (objectif: éliminer tous les ennemis)
- **Mafia** (objectif: majorité mafia)
- **Neutral Evil/Killing** (objectifs variés)
- **Neutral Benign** (objectifs de survie)

### 3. **SYSTÈME DE COMMUNICATION AVANCÉ** (Priorité: HAUTE)
#### **Manquant:**
- Chat nocturne Mafia (entre mafia membres)
- Messages privés avec notification publique
- Système de whisper
- Chat des morts
- Jail chat (entre Jailor et prisonnier)

### 4. **MÉCANIQUES DE JEU AVANCÉES** (Priorité: HAUTE)
#### **Actions multiples par nuit:**
- Actuellement: 1 action par joueur maximum
- Mafia SC2: Plusieurs actions simultanées par faction

#### **Système d'immunités:**
- Defense (Basic/Powerful)
- Attack (Basic/Powerful/Unstoppable)
- Piercing attacks
- Healing
- Detection immunity

#### **Mécaniques spéciales:**
- Jailing (emprisonner un joueur)
- Blackmail (empêcher de parler)
- Roleblock (bloquer l'action)
- Transport (échanger deux joueurs)
- Disguise (changer d'apparence)

### 5. **SYSTÈME DE MAYOR/JAILOR** (Priorité: MOYENNE)
#### **Mayor:**
- Révélation publique
- Vote compte double/triple
- Ne peut pas être soigné après révélation

#### **Jailor:**
- Emprisonne un joueur la nuit
- Peut exécuter les prisonniers
- Chat privé avec le prisonnier

### 6. **AMÉLIORATIONS UX/UI** (Priorité: MOYENNE)
#### **Manquant:**
- Graveyard avec causes de mort détaillées
- Journal des actions détaillé
- Historique des votes
- Interface de sélection de rôles (Custom roles)
- Lobby avec paramètres de partie
- Spectateur mode

---

## 🔥 **PLAN D'IMPLÉMENTATION PRIORITAIRE**

### **PHASE 1: EXPANSION DES RÔLES (4 semaines)**
1. **Semaine 1-2: Rôles Mafia de base**
   - Godfather (immunité investigation)
   - Mafioso (tueur mafia)
   - Consigliere (investigation mafia)
   - Blackmailer (silence les joueurs)

2. **Semaine 3-4: Rôles Town essentiels**
   - Jailor (emprisonnement + exécution)
   - Mayor (révélation + votes multiples)
   - Bodyguard (protection avec sacrifice)
   - Medium (communication avec les morts)

### **PHASE 2: SYSTÈME DE COMMUNICATION (2 semaines)**
1. **Chat nocturne Mafia**
2. **Messages privés publics**
3. **Chat des morts**
4. **Jail chat**

### **PHASE 3: MÉCANIQUES AVANCÉES (3 semaines)**
1. **Système immunités/attaques**
2. **Actions de roleblock/transport**
3. **Système de disguise**
4. **Mécaniques de détection**

### **PHASE 4: RÔLES NEUTRES (2 semaines)**
1. **Serial Killer, Arsonist**
2. **Executioner, Jester**
3. **Survivor, Amnesiac**

---

## 📈 **MÉTRIQUES DE PROGRESSION**

### **Score Actuel: 35/100**
- Mécaniques de base: 8/10
- Variété des rôles: 2/10
- Système de communication: 4/10
- UX/Interface: 7/10
- Fidélité Mafia SC2: 4/10

### **Objectif Final: 95/100**
- 45+ rôles implémentés
- 4 factions équilibrées  
- Communication complète
- Interface polished
- Mécaniques avancées

---

## 💡 **RECOMMANDATIONS IMMÉDIATES**

1. **Corriger les bugs actuels** (investigation panel, chat)
2. **Implémenter chat nocturne Mafia** 
3. **Ajouter 4 rôles Mafia de base**
4. **Créer système d'immunités simple**
5. **Améliorer UX avec graveyard détaillé**

**Temps estimé pour atteindre 80% de fidélité:** 12-16 semaines de développement intensif.

---

*Document créé le: [Date actuelle]*
*Version: 1.0*
*Statut: Analyse complète - Prêt pour développement*