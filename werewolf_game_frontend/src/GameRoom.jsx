import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { ScrollArea } from './components/ui/scroll-area';
import { Alert, AlertDescription } from './components/ui/alert';
import {
  Users,
  MessageCircle,
  Send,
  Clock,
  Skull,
  Eye,
  Shield,
  Zap,
  Target,
  Moon,
  Sun,
  Vote,
  Crown,
  AlertTriangle,
  Play,
  CheckCircle,
  BookOpen,
  Sparkles,
  Sword,
  Heart,
  Crosshair,
} from 'lucide-react';
import './animations.css';

const API_BASE_URL = 'http://localhost:5000/api';

// Obtenir l'icône pour chaque type d'action
const getActionIcon = (actionType) => {
  const icons = {
    kill: Skull,
    see: Eye,
    protect: Shield,
    heal: Heart,
    poison: Zap,
    vote: Vote,
  };
  return icons[actionType] || Target;
};

// Générer une couleur aléatoire pour chaque joueur
const generatePlayerColor = (playerName) => {
  const colors = [
    '#3b82f6', // blue
    '#ef4444', // red
    '#10b981', // emerald
    '#f59e0b', // amber
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#f97316', // orange
    '#84cc16', // lime
    '#ec4899', // pink
    '#6b7280', // gray
  ];

  let hash = 0;
  for (let i = 0; i < playerName.length; i++) {
    hash = playerName.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

const ROLE_DESCRIPTIONS = {
  villager: {
    name: 'Villageois',
    description: 'Citoyen innocent du village',
    detailedDescription:
      "Votre objectif est d'éliminer tous les loups-garous. Vous n'avez aucun pouvoir spécial, mais vous pouvez voter lors des phases de jour.",
    icon: Users,
    color: 'text-blue-400',
    team: 'village',
    glowClass: '',
  },
  werewolf: {
    name: 'Loup-Garou',
    description: 'Créature nocturne qui dévore les villageois',
    detailedDescription:
      "Votre objectif est d'éliminer tous les villageois. Chaque nuit, vous choisissez avec votre équipe une victime à éliminer.",
    icon: Skull,
    color: 'text-red-400',
    team: 'werewolf',
    glowClass: 'werewolf-glow',
  },
  seer: {
    name: 'Voyant',
    description: 'Oracle qui voit au-delà des apparences',
    detailedDescription:
      "Chaque nuit, vous pouvez découvrir le véritable rôle d'un joueur. Utilisez cette information pour guider le village.",
    icon: Eye,
    color: 'text-purple-400',
    team: 'village',
    glowClass: 'seer-glow',
  },
  witch: {
    name: 'Sorcière',
    description: 'Maîtresse des potions magiques',
    detailedDescription:
      'Vous possédez une potion de guérison et une potion de poison à utiliser une seule fois chacune pendant la partie.',
    icon: Zap,
    color: 'text-green-400',
    team: 'village',
    glowClass: 'witch-glow',
  },
  guard: {
    name: 'Garde',
    description: 'Protecteur vigilant du village',
    detailedDescription:
      'Chaque nuit, vous pouvez protéger un joueur des attaques des loups-garous. Vous ne pouvez pas protéger la même personne deux nuits consécutives.',
    icon: Shield,
    color: 'text-yellow-400',
    team: 'village',
    glowClass: 'guard-glow',
  },
  hunter: {
    name: 'Chasseur',
    description: 'Vengeur implacable',
    detailedDescription:
      'Si vous êtes éliminé (par vote ou par les loups), vous pouvez choisir un joueur à éliminer avec vous.',
    icon: Target,
    color: 'text-orange-400',
    team: 'village',
    glowClass: '',
  },
};

const PHASE_INFO = {
  waiting: {
    name: 'Attente',
    description: 'En attente de joueurs',
    icon: Clock,
    color: 'text-blue-200',
    bgClass: 'night-phase',
    duration: 0,
  },
  night: {
    name: 'Nuit',
    description: "Les créatures de la nuit agissent dans l'ombre",
    icon: Moon,
    color: 'text-blue-200',
    bgClass: 'night-phase',
    duration: 60,
  },
  day: {
    name: 'Jour',
    description: 'Le village se réunit pour discuter',
    icon: Sun,
    color: 'text-yellow-200',
    bgClass: 'day-phase-blue',
    duration: 120,
  },
  voting: {
    name: 'Vote',
    description: 'Le moment de la justice est arrivé',
    icon: Vote,
    color: 'text-red-200',
    bgClass: 'voting-phase',
    duration: 60,
  },
  trial: {
    name: 'Procès',
    description: 'Un suspect défend sa vie',
    icon: Crown,
    color: 'text-orange-200',
    bgClass: 'trial-phase',
    duration: 60,
  },
  lynching: {
    name: 'Exécution',
    description: 'Justice est rendue',
    icon: Sword,
    color: 'text-red-300',
    bgClass: 'lynching-phase',
    duration: 10,
  },
  events: {
    name: 'Événements',
    description: 'Révélation des événements nocturnes',
    icon: Sparkles,
    color: 'text-purple-200',
    bgClass: 'events-phase',
    duration: 10,
  },
};

// Chat flottant permanent
const FloatingChat = ({
  chatMessages,
  newMessage,
  setNewMessage,
  sendChatMessage,
  playerName,
  playerColors,
  gamePhase,
  playerAlive,
}) => {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Désactiver le chat pendant la nuit ou si le joueur est mort
  const canChat = gamePhase !== 'night' && playerAlive;

  return (
    <div className="fixed bottom-4 left-4 w-[40rem] h-96 bg-slate-800/95 border border-slate-600 rounded-lg backdrop-blur-md z-50 shadow-2xl">
      <div className="flex items-center justify-between p-3 border-b border-slate-600">
        <div className="flex items-center space-x-2">
          <MessageCircle className="w-4 h-4 text-blue-400" />
          <span className="text-white font-medium text-sm">
            Chat du Village
          </span>
        </div>
        {!canChat && (
          <Badge variant="secondary" className="text-xs">
            {gamePhase === 'night' ? 'Nuit' : 'Silencieux'}
          </Badge>
        )}
      </div>

      <ScrollArea className="h-64 p-3">
        {chatMessages.length === 0 ? (
          <p className="text-slate-400 text-center text-sm">
            Le village est silencieux...
          </p>
        ) : (
          <div className="space-y-2">
            {chatMessages.map((msg, index) => {
              const playerName = msg.player || msg.player_name || 'Joueur';
              const message = msg.message || '';
              return (
                <div
                  key={`chat-${index}-${msg.timestamp || Date.now()}`}
                  className="text-sm"
                >
                  <span
                    className="font-medium"
                    style={{ color: playerColors[playerName] || '#94a3b8' }}
                  >
                    {playerName}:
                  </span>
                  <span className="text-white ml-2">{message}</span>
                </div>
              );
            })}
            <div ref={chatEndRef} />
          </div>
        )}
      </ScrollArea>

      <div
        className={`p-3 border-t border-slate-600 ${
          !canChat ? 'opacity-50' : ''
        }`}
      >
        {!canChat && (
          <p className="text-slate-400 text-xs mb-2 text-center">
            {gamePhase === 'night'
              ? 'Le chat est désactivé pendant la nuit'
              : 'Vous ne pouvez plus parler'}
          </p>
        )}
        <div className="flex space-x-2">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={canChat ? 'Tapez votre message...' : 'Chat désactivé'}
            className="bg-slate-700/50 border-slate-600 text-white text-sm"
            onKeyPress={(e) =>
              e.key === 'Enter' && canChat && sendChatMessage()
            }
            disabled={!canChat}
          />
          <Button
            onClick={sendChatMessage}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700"
            disabled={!canChat}
          >
            <Send className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  );
};

// Guide des rôles
const RoleGuide = () => {
  return (
    <Card className="bg-slate-800/90 border-slate-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <BookOpen className="w-5 h-5" />
          <span>Guide des Rôles</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {Object.entries(ROLE_DESCRIPTIONS).map(([key, role]) => {
            const RoleIcon = role.icon;
            return (
              <div
                key={key}
                className="flex items-start space-x-3 p-2 bg-slate-700/30 rounded-lg role-guide-item"
              >
                <RoleIcon className={`w-4 h-4 ${role.color} mt-0.5`} />
                <div>
                  <h4 className="text-white font-medium text-sm">
                    {role.name}
                  </h4>
                  <p className="text-slate-400 text-xs">{role.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

// 🆕 Panel de Procès
const TrialPanel = ({ gameState, playerName, onTrialVote, trialInfo }) => {
  const [hasVoted, setHasVoted] = useState(false);
  const [verdict, setVerdict] = useState(null);

  const accusedPlayer = gameState?.accused_player || trialInfo?.accused_player;
  const isAccused = playerName === accusedPlayer;
  const canVote = !isAccused && !hasVoted && gameState?.players?.find(p => p.name === playerName)?.alive;

  const handleVote = async (selectedVerdict) => {
    if (!canVote) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/games/${gameState.id}/trial-vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name: playerName,
          verdict: selectedVerdict
        })
      });

      if (response.ok) {
        setHasVoted(true);
        setVerdict(selectedVerdict);
        onTrialVote?.(selectedVerdict);
      }
    } catch (error) {
      console.error('Erreur vote procès:', error);
    }
  };

  // Calculer les votes
  const votesCounts = Object.values(trialInfo?.trial_votes || {}).reduce((acc, vote) => {
    acc[vote] = (acc[vote] || 0) + 1;
    return acc;
  }, {});

  const guiltyVotes = votesCounts.GUILTY || 0;
  const innocentVotes = votesCounts.INNOCENT || 0;
  const totalVotes = guiltyVotes + innocentVotes;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 trial-overlay">
      <Card className="w-full max-w-2xl mx-4 bg-gradient-to-br from-amber-900/90 to-red-900/90 border-amber-700/50 backdrop-blur-md">
        <CardHeader className="text-center border-b border-amber-700/30">
          <div className="flex items-center justify-center space-x-3 mb-2">
            <Crown className="w-8 h-8 text-amber-400" />
            <CardTitle className="text-2xl font-bold text-amber-100">
              PROCÈS EN COURS
            </CardTitle>
            <Crown className="w-8 h-8 text-amber-400" />
          </div>
          <CardDescription className="text-amber-200 text-lg">
            {accusedPlayer} est accusé(e) et doit défendre sa vie !
          </CardDescription>
        </CardHeader>

        <CardContent className="p-6">
          {/* Accusé en spotlight */}
          <div className="text-center mb-6 p-4 bg-amber-800/30 rounded-lg border border-amber-600/30">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-red-600/80 rounded-full mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-300" />
              <span className="text-white font-bold">ACCUSÉ(E)</span>
            </div>
            <h3 className="text-xl font-bold text-amber-100 mb-2">{accusedPlayer}</h3>
            {isAccused ? (
              <p className="text-amber-200 italic">
                Votre vie est entre les mains du village. Défendez-vous !
              </p>
            ) : (
              <p className="text-amber-200">
                Écoutez sa défense et rendez votre verdict
              </p>
            )}
          </div>

          {/* Votes si pas l'accusé */}
          {!isAccused && (
            <div className="space-y-4">
              <h4 className="text-amber-100 font-semibold text-center">
                Votre Verdict :
              </h4>
              
              {!hasVoted ? (
                <div className="flex justify-center space-x-4">
                  <Button
                    onClick={() => handleVote('innocent')}
                    className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 text-lg font-bold"
                    disabled={!canVote}
                  >
                    <CheckCircle className="w-5 h-5 mr-2" />
                    INNOCENT
                  </Button>
                  <Button
                    onClick={() => handleVote('guilty')}
                    className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 text-lg font-bold"
                    disabled={!canVote}
                  >
                    <Crosshair className="w-5 h-5 mr-2" />
                    COUPABLE
                  </Button>
                </div>
              ) : (
                <div className="text-center">
                  <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full ${
                    verdict === 'guilty' ? 'bg-red-600/80' : 'bg-green-600/80'
                  }`}>
                    {verdict === 'guilty' ? (
                      <Crosshair className="w-5 h-5 text-white" />
                    ) : (
                      <CheckCircle className="w-5 h-5 text-white" />
                    )}
                    <span className="text-white font-bold">
                      Vous avez voté {verdict === 'guilty' ? 'COUPABLE' : 'INNOCENT'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Décompte des votes */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="bg-green-900/30 border border-green-600/30 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-400">{innocentVotes}</div>
              <div className="text-green-300 text-sm">INNOCENT</div>
            </div>
            <div className="bg-red-900/30 border border-red-600/30 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-400">{guiltyVotes}</div>
              <div className="text-red-300 text-sm">COUPABLE</div>
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-4 text-center text-amber-300 text-sm">
            {isAccused ? (
              "Vous ne pouvez pas voter à votre propre procès"
            ) : canVote ? (
              "Choisissez votre verdict - La majorité décide du sort de l'accusé(e)"
            ) : hasVoted ? (
              "Vote enregistré - En attente des autres joueurs"
            ) : (
              "Vous ne pouvez pas voter (mort ou déjà voté)"
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Cimetière
const Cemetery = ({ gameState }) => {
  const deadPlayers = gameState?.players?.filter((p) => !p.alive) || [];

  // Obtenir le nom d'affichage du rôle
  const getRoleDisplayName = (role) => {
    const roleNames = {
      villager: 'Villageois',
      werewolf: 'Loup-Garou',
      seer: 'Voyant',
      witch: 'Sorcière',
      guard: 'Garde',
      bodyguard: 'Garde',
      hunter: 'Chasseur',
    };
    return roleNames[role] || role;
  };

  // Obtenir l'icône selon le rôle
  const getRoleIcon = (role) => {
    const roleIcons = {
      villager: '👤', // Personne simple
      werewolf: '🐺', // Loup
      seer: '👁️', // Œil
      witch: '🧙‍♀️', // Sorcière
      guard: '🛡️', // Bouclier
      bodyguard: '🛡️', // Bouclier
      hunter: '🏹', // Arc
    };
    return roleIcons[role] || '👤';
  };

  return (
    <Card className="bg-slate-800/90 border-slate-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <span className="text-lg">⚰️</span>
          <span>Cimetière ({deadPlayers.length})</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {deadPlayers.length === 0 ? (
            <p className="text-slate-500 text-sm italic">
              Aucun mort pour l'instant...
            </p>
          ) : (
            deadPlayers.map((player, index) => (
              <div
                key={player.name || `dead-${index}`}
                className="flex items-center space-x-2 p-2 bg-slate-900/50 rounded-lg cemetery-item"
              >
                <span className="text-lg">{getRoleIcon(player.role)}</span>
                <span className="text-slate-300 text-sm line-through">
                  {player.name || player.player_name} -{' '}
                  {getRoleDisplayName(player.role)}
                </span>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

function GameRoom({ roomCode, playerName, onLeaveGame }) {
  const [gameState, setGameState] = useState(null);
  const [playerRole, setPlayerRole] = useState(null);
  const [availableActions, setAvailableActions] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastPhase, setLastPhase] = useState(null);
  const [showPhaseTransition, setShowPhaseTransition] = useState(false);
  const [showDayOverlay, setShowDayOverlay] = useState(false);
  const [actionFeedback, setActionFeedback] = useState('');
  const [lobbyPlayers, setLobbyPlayers] = useState([]);
  const [playerColors, setPlayerColors] = useState({});
  const [phaseEvents, setPhaseEvents] = useState('');
  const chatEndRef = useRef(null);
  const [currentVote, setCurrentVote] = useState(null);
  const [voteHistory, setVoteHistory] = useState([]);
  const [selectedActions, setSelectedActions] = useState({}); // Actions sélectionnées pour affichage visuel
  const [showCountdown, setShowCountdown] = useState(false);
  const [countdownNumber, setCountdownNumber] = useState(3);
  const [showGameStartAnimation, setShowGameStartAnimation] = useState(false);
  const [showNightAnimation, setShowNightAnimation] = useState(false);
  const [showDayAnimation, setShowDayAnimation] = useState(false);
  
  // 🆕 États pour le système de procès
  const [trialInfo, setTrialInfo] = useState(null);
  const [showTrialPanel, setShowTrialPanel] = useState(false);

  useEffect(() => {
    fetchGameData();
    const interval = setInterval(fetchGameData, 1000);
    return () => clearInterval(interval);
  }, [roomCode, playerName]);

  useEffect(() => {
    // Handle phase transitions avec animations pleine écran
    if (lastPhase && gameState && lastPhase !== gameState.phase) {
      // Clear les événements lors du changement de phase
      setPhaseEvents('');

      // Animation spécifique pour le passage à la phase jour
      if (gameState.phase === 'day') {
        setShowDayAnimation(true);
        setTimeout(() => setShowDayAnimation(false), 3000);
      } else if (gameState.phase === 'night') {
        setShowNightAnimation(true);
        setTimeout(() => setShowNightAnimation(false), 3000);
      } else if (gameState.phase === 'trial') {
        // 🆕 Ouvrir le panel de procès
        setShowTrialPanel(true);
        fetchTrialInfo();
      } else if (gameState.phase === 'lynching') {
        // 🆕 Fermer le panel de procès pendant l'exécution
        setShowTrialPanel(false);
      }
    }
    setLastPhase(gameState?.phase);
  }, [gameState?.phase]);

  // 🆕 Fonction pour récupérer les infos du procès
  const fetchTrialInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${roomCode}/trial-info`);
      if (response.ok) {
        const data = await response.json();
        setTrialInfo(data);
      }
    } catch (error) {
      console.error('Erreur récupération info procès:', error);
    }
  };

  // Générer les couleurs des joueurs au début
  useEffect(() => {
    if (gameState?.players && Object.keys(playerColors).length === 0) {
      const colors = {};
      gameState.players.forEach((player) => {
        // Support pour différents formats de données joueur
        const playerName = player.name || player.player_name || player;
        if (playerName && typeof playerName === 'string') {
          colors[playerName] = generatePlayerColor(playerName);
        }
      });
      setPlayerColors(colors);
    }
  }, [gameState?.players]);

  const fetchGameData = async () => {
    try {
      setError(null);

      // First get basic game info
      const gameResponse = await fetch(`${API_BASE_URL}/games/${roomCode}`);
      if (!gameResponse.ok) {
        throw new Error('Partie non trouvée');
      }
      const gameData = await gameResponse.json();

      // If game is still waiting, show lobby
      if (gameData.status === 'waiting') {
        setLobbyPlayers(gameData.players || []);
        setGameState({ ...gameData, phase: 'waiting' });
        setLoading(false);
        return;
      }

      // If game has started, get full game state
      const gameStateResponse = await fetch(
        `${API_BASE_URL}/games/${roomCode}/state`
      );

      if (!gameStateResponse.ok) {
        if (gameStateResponse.status === 500) {
          // Essayer de récupérer les informations de base du jeu
          setGameState(gameData);
          setError('Reconnexion en cours...');
          setTimeout(() => setError(''), 3000);
          return;
        }
        throw new Error('Erreur lors du chargement des données');
      }

      const gameStateData = await gameStateResponse.json();

      // Get player role and actions
      const [playerRoleResponse, actionsResponse] = await Promise.all([
        fetch(
          `${API_BASE_URL}/games/${roomCode}/player/${playerName}/role`
        ).catch(() => null),
        fetch(
          `${API_BASE_URL}/games/${roomCode}/player/${playerName}/actions`
        ).catch(() => null),
      ]);

      let playerRoleData = null;
      let actionsData = { actions: [] };

      if (playerRoleResponse && playerRoleResponse.ok) {
        playerRoleData = await playerRoleResponse.json();
      }

      if (actionsResponse && actionsResponse.ok) {
        actionsData = await actionsResponse.json();
      }

      // Détecter les changements de phase pour afficher la transition
      if (
        lastPhase &&
        lastPhase !== gameStateData.phase &&
        gameStateData.phase !== 'waiting'
      ) {
        // Animation spécifique pour le passage à la phase jour
        if (gameStateData.phase === 'day') {
          setShowDayOverlay(true);
          setTimeout(() => setShowDayOverlay(false), 3000);
        } else {
          setShowPhaseTransition(true);
          setTimeout(() => setShowPhaseTransition(false), 3000);
        }

        // Mettre à jour les événements de phase si disponibles
        if (gameStateData.last_phase_events) {
          setPhaseEvents(gameStateData.last_phase_events);
        }
      }
      setLastPhase(gameStateData.phase);

      setGameState(gameStateData);
      setPlayerRole(playerRoleData);
      setAvailableActions(actionsData.actions || []);
      setChatMessages(gameStateData.chat_messages || []);

      setLoading(false);
    } catch (err) {
      console.error('Error fetching game data:', err);
      setError(err.message);
      setTimeout(() => setError(''), 5000);
      setLoading(false);
    }
  };

  const startGame = async () => {
    try {
      // Lancer le countdown avant de démarrer la partie
      setShowCountdown(true);

      const countdownSequence = () => {
        let count = 3;
        setCountdownNumber(count);

        const countdownInterval = setInterval(() => {
          count--;
          if (count > 0) {
            setCountdownNumber(count);
          } else {
            clearInterval(countdownInterval);
            setShowCountdown(false);
            setShowGameStartAnimation(true);

            // Faire la requête pour démarrer la partie
            startGameRequest();

            // Cacher l'animation après 3 secondes
            setTimeout(() => {
              setShowGameStartAnimation(false);
            }, 3000);
          }
        }, 1000);
      };

      countdownSequence();
    } catch (err) {
      console.error('Error starting game:', err);
      setError('Erreur lors du démarrage de la partie');
    }
  };

  const startGameRequest = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${roomCode}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setActionFeedback('Partie démarrée avec succès !');
        setTimeout(() => setActionFeedback(''), 3000);
        fetchGameData();
      } else {
        setError(data.error || 'Erreur lors du démarrage de la partie');
        setTimeout(() => setError(''), 5000);
      }
    } catch (err) {
      console.error('Error starting game:', err);
      setError('Erreur lors du démarrage de la partie');
      setTimeout(() => setError(''), 5000);
    }
  };

  const performAction = async (actionType, target = null) => {
    try {
      // Déterminer l'endpoint basé sur la phase et le type d'action
      let endpoint;
      let payload;

      if (
        actionType === 'vote' ||
        gameState?.phase === 'day' ||
        gameState?.phase === 'voting'
      ) {
        endpoint = `${API_BASE_URL}/games/${roomCode}/vote`;
        payload = {
          player_name: playerName,
          target: target,
        };
      } else {
        endpoint = `${API_BASE_URL}/games/${roomCode}/night-action`;
        payload = {
          player_name: playerName,
          action: actionType,
          target: target,
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setActionFeedback(data.message || 'Action effectuée avec succès');
        setTimeout(() => setActionFeedback(''), 3000);

        // Mettre à jour le vote actuel si c'est un vote
        if (actionType === 'vote' || endpoint.includes('/vote')) {
          setCurrentVote(target);
        } else {
          // Mettre à jour l'action sélectionnée pour l'affichage visuel
          setSelectedActions((prev) => ({
            ...prev,
            [actionType]: target,
          }));
        }

        fetchGameData();
      } else {
        setError(data.error || "Erreur lors de l'action");
        setTimeout(() => setError(''), 5000);
      }
    } catch (err) {
      console.error('Error performing action:', err);
      setError("Erreur lors de l'action");
      setTimeout(() => setError(''), 5000);
    }
  };

  const castVote = async (target) => {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${roomCode}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_name: playerName,
          target: target,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erreur lors du vote');
      }

      // Pas de message de feedback pour le vote - reste discret
      setCurrentVote(target);
    } catch (err) {
      console.error('Error casting vote:', err);
      setError(err.message);
    }
  };

  // 🆕 Gestion du vote de procès
  const handleTrialVote = (verdict) => {
    console.log('Vote procès:', verdict);
    // Rafraîchir les infos du procès après vote
    setTimeout(() => {
      fetchTrialInfo();
    }, 500);
  };

  const sendChatMessage = async () => {
    if (!newMessage.trim()) return;

    // Empêcher l'envoi de messages pendant la nuit
    if (gameState?.phase === 'night') {
      setError('Le chat est désactivé pendant la nuit');
      setTimeout(() => setError(''), 3000);
      return;
    }

    // Empêcher l'envoi si le joueur est mort
    if (playerRole?.alive === false) {
      setError('Les morts ne peuvent plus parler');
      setTimeout(() => setError(''), 3000);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/games/${roomCode}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_name: playerName,
          message: newMessage.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setNewMessage('');
          // Mettre à jour les messages de chat directement si disponibles
          if (data.chat_messages) {
            setChatMessages(data.chat_messages);
          }
          // Rafraîchir les données de jeu
          fetchGameData();
        } else {
          setError(data.error || "Erreur lors de l'envoi du message");
          setTimeout(() => setError(''), 3000);
        }
      } else {
        // Essayer de récupérer le message d'erreur du serveur
        try {
          const errorData = await response.json();
          setError(errorData.error || "Erreur lors de l'envoi du message");
        } catch {
          setError("Erreur lors de l'envoi du message");
        }
        setTimeout(() => setError(''), 3000);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Erreur de connexion');
      setTimeout(() => setError(''), 3000);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    if (!gameState?.remaining_time || !gameState?.phase_duration) return 0;
    return (
      ((gameState.phase_duration - gameState.remaining_time) /
        gameState.phase_duration) *
      100
    );
  };

  const isTimerCritical = () => {
    return gameState?.remaining_time <= 10;
  };

  // Génération d'événements améliorée - seulement les vrais événements
  const generateEventMessage = () => {
    if (!gameState) return null;

    // Filtrer seulement les vrais événements (pas les changements de phase)
    if (gameState.game_history && gameState.game_history.length > 0) {
      // Prendre seulement les événements de la phase précédente
      const currentDay = gameState.day_count || 1;
      const relevantEvents = gameState.game_history.filter((event) => {
        // Garder les événements récents et significatifs
        return (
          event.type !== 'phase_change' &&
          (event.day === currentDay || event.day === currentDay - 1) &&
          (event.type === 'elimination' ||
            event.type === 'random_event' ||
            event.type === 'night_action')
        );
      });

      // Enrichir les événements avec les rôles des joueurs morts
      const enrichedEvents = relevantEvents.map((event) => {
        if (event.type === 'elimination' && event.player_name) {
          const deadPlayer = gameState.players.find(
            (p) => (p.name || p.player_name) === event.player_name
          );
          if (deadPlayer && deadPlayer.role) {
            return {
              ...event,
              description: `${event.description}\nRôle : ${getRoleDisplayName(
                deadPlayer.role
              )}`,
            };
          }
        }
        return event;
      });

      if (enrichedEvents.length > 0) {
        return enrichedEvents.slice(-3);
      }
    }

    // Messages par défaut selon la phase avec immersion loup-garou
    if (gameState.phase === 'day') {
      const dayNumber = gameState.day_count || 1;
      if (dayNumber === 1) {
        return [
          {
            type: 'peaceful_night',
            description:
              'Le village dort tranquillement. Les habitants ne se doutent de rien...',
            phase: 'night',
          },
        ];
      } else {
        return [
          {
            type: 'peaceful_night',
            description:
              "La nuit s'est écoulée sans incident. Les créatures de la nuit sont restées cachées.",
            phase: 'night',
          },
        ];
      }
    } else if (gameState.phase === 'events' || gameState.phase === 'night') {
      return [
        {
          type: 'peaceful_day',
          description:
            "Le jour s'est écoulé paisiblement. Les villageois vaquent à leurs occupations.",
          phase: 'day',
        },
      ];
    }

    return null;
  };

  // Obtenir le nom d'affichage du rôle
  const getRoleDisplayName = (role) => {
    const roleNames = {
      villager: 'Villageois',
      werewolf: 'Loup-Garou',
      seer: 'Voyant',
      witch: 'Sorcière',
      guard: 'Garde',
      bodyguard: 'Garde',
      hunter: 'Chasseur',
    };
    return roleNames[role] || role;
  };

  // Compter les votes pour chaque joueur
  const getVoteCounts = () => {
    const voteCounts = {};
    if (gameState?.players) {
      gameState.players.forEach((player) => {
        if (player.vote_target) {
          voteCounts[player.vote_target] =
            (voteCounts[player.vote_target] || 0) + 1;
        }
      });
    }
    return voteCounts;
  };

  // Obtenir le titre d'action selon le rôle avec immersion
  const getActionTitle = () => {
    if (!playerRole?.role) return 'Vous êtes villageois, qui soupçonnez-vous ?';

    const actionTitles = {
      werewolf:
        'Vous êtes loup-garou, qui choisirez-vous de dévorer cette nuit ?',
      seer: 'Vous êtes voyant, de qui voulez-vous connaître la véritable nature ?',
      witch: 'Vous êtes sorcière, utiliserez-vous vos potions cette nuit ?',
      guard: 'Vous êtes garde, qui protégerez-vous des ténèbres ?',
      bodyguard: 'Vous êtes garde du corps, qui défendrez-vous ?',
      hunter: 'Vous êtes chasseur, qui voulez-vous éliminer ?',
      villager: 'Vous êtes villageois, qui soupçonnez-vous ?',
    };

    return (
      actionTitles[playerRole.role] ||
      'Vous êtes villageois, qui soupçonnez-vous ?'
    );
  };

  // Compter le total des joueurs vivants pour les votes
  const getTotalAlivePlayers = () => {
    return gameState?.players?.filter((p) => p.alive).length || 0;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">
          Chargement de la partie...
        </div>
      </div>
    );
  }

  if (error && !gameState) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <Card className="bg-slate-800 border-slate-700 card-enter">
          <CardContent className="p-6">
            <div className="text-red-400 text-center">
              <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
              <p className="text-xl mb-4">Erreur</p>
              <p className="mb-4">{error}</p>
              <Button
                onClick={onLeaveGame}
                className="bg-red-600 hover:bg-red-700 text-white border-red-600"
              >
                Retour au lobby
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show lobby if game is waiting
  if (gameState && gameState.status === 'waiting') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
        <div className="container mx-auto max-w-4xl">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="card-enter">
              <h1 className="text-3xl font-bold text-white drop-shadow-lg">
                {gameState.name}
              </h1>
              <p className="text-blue-200">
                Salle: {roomCode} • En attente de joueurs
              </p>
            </div>
            <Button
              onClick={onLeaveGame}
              className="bg-red-600 hover:bg-red-700 text-white border-red-600"
            >
              Quitter la salle
            </Button>
          </div>

          {/* Error/Success feedback */}
          {(error || actionFeedback) && (
            <Alert
              className={`mb-4 card-enter ${
                error ? 'border-red-500' : 'border-green-500'
              }`}
            >
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription
                className={error ? 'text-red-400' : 'text-green-400'}
              >
                {error || actionFeedback}
              </AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Players List */}
            <Card className="bg-slate-800/90 border-slate-700 card-enter backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>
                    Joueurs ({lobbyPlayers.length}/{gameState.max_players})
                  </span>
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Minimum 4 joueurs requis pour commencer
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {lobbyPlayers.map((player) => (
                    <div
                      key={player.player_name}
                      className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-white font-medium">
                          {player.player_name}
                          {player.player_name === playerName && ' (Vous)'}
                        </span>
                      </div>
                      {player.is_ready && (
                        <Badge className="bg-green-600">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Prêt
                        </Badge>
                      )}
                    </div>
                  ))}

                  {/* Empty slots */}
                  {Array.from({
                    length: gameState.max_players - lobbyPlayers.length,
                  }).map((_, index) => (
                    <div
                      key={`empty-${index}`}
                      className="flex items-center p-3 bg-slate-800/50 rounded-lg border-2 border-dashed border-slate-600"
                    >
                      <div className="w-3 h-3 bg-slate-600 rounded-full mr-3"></div>
                      <span className="text-slate-500 italic">
                        En attente d'un joueur...
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Game Info & Start */}
            <Card className="bg-slate-800/90 border-slate-700 card-enter backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white">
                  Lancement de la Partie
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Prêt à commencer l'aventure ?
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-slate-300">
                  <h4 className="font-medium mb-2">Configuration:</h4>
                  <ul className="text-sm space-y-1 text-slate-400">
                    <li>
                      • Joueurs: {lobbyPlayers.length}/{gameState.max_players}
                    </li>
                    <li>• Rôles assignés automatiquement</li>
                    <li>• Phases: Nuit → Jour → Vote</li>
                    <li>• Communication temps réel</li>
                  </ul>
                </div>

                <div className="pt-4 border-t border-slate-600">
                  {lobbyPlayers.length >= 4 ? (
                    <Button
                      onClick={startGame}
                      className="w-full bg-green-600 hover:bg-green-700 text-white"
                      size="lg"
                    >
                      <Play className="w-5 h-5 mr-2" />
                      Démarrer la Partie
                    </Button>
                  ) : (
                    <div className="text-center">
                      <Button disabled className="w-full" size="lg">
                        <Users className="w-5 h-5 mr-2" />
                        {4 - lobbyPlayers.length} joueur(s) manquant(s)
                      </Button>
                      <p className="text-xs text-slate-500 mt-2">
                        Partagez le code{' '}
                        <span className="font-mono bg-slate-700 px-2 py-1 rounded">
                          {roomCode}
                        </span>{' '}
                        avec vos amis
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (!gameState || !playerRole) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Données de jeu non disponibles</div>
      </div>
    );
  }

  const currentPhase = PHASE_INFO[gameState.phase] || {
    name: gameState.phase,
    icon: Clock,
    color: 'text-gray-400',
    bgClass: 'night-phase',
  };

  // Classe CSS pour les transitions douces entre phases
  const getTransitionClass = () => {
    if (gameState?.transition_type) {
      switch (gameState.transition_type) {
        case 'night_results':
          return 'events-phase';
        case 'day_results':
          return 'events-phase';
        default:
          return currentPhase.bgClass;
      }
    }
    return currentPhase.bgClass;
  };

  const roleInfo = ROLE_DESCRIPTIONS[playerRole.role] || {
    name: playerRole.role,
    icon: Users,
    color: 'text-gray-400',
    glowClass: '',
  };

  const RoleIcon = roleInfo.icon;
  const PhaseIcon = currentPhase.icon;
  const alivePlayersCount =
    gameState.players?.filter((p) => p.alive).length || 0;
  const totalPlayersCount = gameState.players?.length || 0;
  const voteCounts = getVoteCounts();
  const eventMessages = generateEventMessage();

  return (
    <div className={`min-h-screen ${getTransitionClass()} relative`}>
      {/* Countdown avant démarrage - thème loup-garou */}
      {showCountdown && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-slate-900 via-red-900 to-black backdrop-blur-sm">
          <div className="text-center">
            <div className="text-6xl mb-4 animate-bounce">🌙</div>
            <div className="text-9xl font-bold text-red-200 animate-pulse countdown-number">
              {countdownNumber}
            </div>
            <p className="text-2xl text-red-100 mt-4">
              La nuit tombe sur le village...
            </p>
            <p className="text-lg text-red-200/80 mt-2">
              Les créatures s'éveillent
            </p>
          </div>
        </div>
      )}

      {/* Animation de démarrage - thème loup-garou */}
      {showGameStartAnimation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-r from-slate-900 via-red-800 to-slate-900 game-start-fade">
          <div className="text-center">
            <div className="text-6xl mb-4 animate-bounce">🐺</div>
            <h2 className="text-4xl font-bold text-red-100 drop-shadow-lg">
              Que la chasse commence !
            </h2>
            <p className="text-xl text-red-200/90 mt-2">
              Les rôles secrets ont été distribués...
            </p>
            <p className="text-lg text-red-300/80 mt-1">
              Qui survivra à cette nuit ?
            </p>
          </div>
        </div>
      )}

      {/* Animation de nuit - thème loup-garou */}
      {showNightAnimation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-r from-slate-900 via-gray-900 to-black night-animation">
          <div className="text-center">
            <div className="text-6xl mb-4 animate-pulse">🌙</div>
            <h2 className="text-4xl font-bold text-blue-100 drop-shadow-lg">
              La nuit tombe sur le village
            </h2>
            <p className="text-xl text-blue-200/90 mt-2">
              Les créatures sortent de l'ombre...
            </p>
            <p className="text-lg text-blue-300/80 mt-1">
              Qui ne verra pas le lever du jour ?
            </p>
          </div>
        </div>
      )}

      {/* Animation de jour - thème loup-garou */}
      {showDayAnimation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-r from-orange-600 via-yellow-500 to-orange-600 day-animation">
          <div className="text-center">
            <div className="text-6xl mb-4 animate-bounce">☀️</div>
            <h2 className="text-4xl font-bold text-orange-100 drop-shadow-lg">
              L'aube se lève sur le village
            </h2>
            <p className="text-xl text-orange-200/90 mt-2">
              Les villageois découvrent ce qui s'est passé...
            </p>
            <p className="text-lg text-orange-300/80 mt-1">
              Qui a survécu à cette nuit ?
            </p>
          </div>
        </div>
      )}

      {/* Chat flottant permanent */}
      <FloatingChat
        chatMessages={chatMessages}
        newMessage={newMessage}
        setNewMessage={setNewMessage}
        sendChatMessage={sendChatMessage}
        playerName={playerName}
        playerColors={playerColors}
        gamePhase={gameState?.phase}
        playerAlive={playerRole?.alive !== false}
      />

      <div className="relative z-10 p-4">
        <div className="container mx-auto max-w-7xl">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="card-enter">
              <h1 className="text-3xl font-bold text-white drop-shadow-lg">
                {gameState.name}
              </h1>
              <p className="text-blue-200">
                Salle: {roomCode} • Jour {gameState.day_count} •{' '}
                {currentPhase.name}
              </p>
            </div>
            <Button
              onClick={onLeaveGame}
              className="bg-red-600 hover:bg-red-700 text-white border-red-600"
            >
              Quitter la partie
            </Button>
          </div>

          {/* Error feedback only (action feedback goes to events) */}
          {error && (
            <Alert className="mb-4 card-enter border-red-500">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-red-400">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Nouvelle mise en page 3 colonnes */}
          <div className="content-grid-3col">
            {/* Colonne Gauche - Guide des rôles + Cimetière */}
            <div className="space-y-6">
              <RoleGuide />
              <Cemetery gameState={gameState} />
            </div>

            {/* Colonne Centrale - Countdown + Événements + Actions */}
            <div className="central-column space-y-6">
              {/* Phase Timer */}
              <div className="timer-display">
                <div className="phase-display">
                  {formatTime(gameState.remaining_time || 0)}
                </div>
                <div className="phase-name">{currentPhase.name}</div>
                {gameState.day_count && (
                  <div className="day-counter">Jour {gameState.day_count}</div>
                )}
                <div className="mt-4">
                  <Progress
                    value={getProgressPercentage()}
                    className="w-full h-3"
                  />
                </div>
              </div>

              {/* Événements de la partie */}
              <Card className="bg-slate-800/90 border-slate-700 card-enter backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    <span>Chronique du Village</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {eventMessages && eventMessages.length > 0 ? (
                      eventMessages.map((event, index) => (
                        <div key={index} className="p-2">
                          <p className="text-slate-300 text-base leading-relaxed">
                            {event.description}
                          </p>
                          {event.day && (
                            <span className="text-slate-500 text-xs">
                              Jour {event.day} - {event.phase}
                            </span>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="p-2">
                        <p className="text-slate-400 text-base italic">
                          Le silence règne sur le village...
                        </p>
                      </div>
                    )}

                    {/* Feedback d'action simplifié */}
                    {actionFeedback && (
                      <div className="p-2">
                        <p className="text-slate-300 text-base">
                          {actionFeedback}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Actions */}
              {playerRole.alive && availableActions.length > 0 && (
                <Card className="bg-slate-800/90 border-slate-700 card-enter card-hover backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center space-x-2">
                      <Target className="w-5 h-5 text-orange-400" />
                      <span>{getActionTitle()}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {availableActions.map((action, index) => {
                      const ActionIcon = getActionIcon(action.type);
                      return (
                        <div key={index} className="space-y-3">
                          <div className="flex items-center space-x-2 mb-2">
                            <ActionIcon className="w-4 h-4 text-blue-400" />
                            <span className="text-white font-medium">
                              {action.name}
                            </span>
                          </div>

                          {action.targets && action.targets.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                              {action.targets.map((target) => {
                                const isSelected =
                                  selectedActions[action.type] === target;
                                return (
                                  <Button
                                    key={target}
                                    onClick={() =>
                                      performAction(action.type, target)
                                    }
                                    className={`action-button ${
                                      isSelected
                                        ? 'selected'
                                        : 'bg-slate-600 hover:bg-slate-700'
                                    }`}
                                    size="sm"
                                  >
                                    {isSelected && '✓ '}
                                    {target}
                                  </Button>
                                );
                              })}
                            </div>
                          )}

                          {action.type === 'heal' && (
                            <Button
                              onClick={() => performAction('heal')}
                              className="bg-slate-600 hover:bg-slate-700 action-button flex items-center space-x-2"
                            >
                              <Heart className="w-4 h-4" />
                              <span>Utiliser la Potion de Guérison</span>
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>
              )}

              {/* Votes durant la phase de vote */}
              {gameState.phase === 'voting' && playerRole.alive && (
                <Card className="bg-slate-800/90 border-slate-700 card-enter backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center space-x-2">
                      <Vote className="w-5 h-5 text-red-400" />
                      <span>Conseil du Village</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {gameState.players
                        .filter((p) => p.alive && p.name !== playerName)
                        .map((player) => (
                          <Button
                            key={player.name}
                            onClick={() => castVote(player.name)}
                            className="w-full bg-slate-600 hover:bg-slate-700 text-white vote-transition"
                            size="sm"
                          >
                            Accuser {player.name}
                          </Button>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Game End */}
              {gameState.winner && (
                <Card className="bg-slate-800/90 border-slate-700 card-enter backdrop-blur-sm">
                  <CardHeader>
                    <div className="flex items-center space-x-2">
                      <Crown className="w-6 h-6 text-yellow-400" />
                      <CardTitle className="text-white">
                        Partie Terminée
                      </CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <p className="text-2xl text-yellow-400 font-bold mb-2 role-reveal">
                        Victoire des{' '}
                        {gameState.winner === 'villagers'
                          ? 'Villageois'
                          : 'Loups-Garous'}{' '}
                        !
                      </p>
                      {gameState.last_elimination && (
                        <p className="text-slate-300">
                          {gameState.last_elimination}
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Colonne Droite - Rôle du joueur + Liste des joueurs */}
            <div className="space-y-6">
              {/* Player Role */}
              <Card
                className={`bg-slate-800/90 border-slate-700 card-enter card-hover backdrop-blur-sm ${roleInfo.glowClass}`}
              >
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full bg-slate-700/50`}>
                      <RoleIcon className={`w-8 h-8 ${roleInfo.color}`} />
                    </div>
                    <div>
                      <CardTitle className="text-white">
                        {roleInfo.name}
                      </CardTitle>
                      <CardDescription className="text-slate-400">
                        {roleInfo.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-300 text-sm mb-3">
                    {roleInfo.detailedDescription}
                  </p>
                  {playerRole.role === 'werewolf' &&
                    playerRole.werewolf_team && (
                      <div className="text-red-400">
                        <p className="font-medium mb-2">Équipe Loup-Garou:</p>
                        <div className="flex flex-wrap gap-2">
                          {playerRole.werewolf_team.map((teammate) => (
                            <Badge
                              key={teammate}
                              variant="destructive"
                              className="animate-pulse"
                            >
                              {teammate}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                </CardContent>
              </Card>

              {/* Players List */}
              <Card className="bg-slate-800/90 border-slate-700 card-enter card-hover backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Users className="w-5 h-5" />
                    <span>
                      Joueurs ({alivePlayersCount}/{totalPlayersCount})
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {gameState.players.map((player, index) => {
                      const playerName_key = player.name || player.player_name;
                      const voteCount = voteCounts[playerName_key] || 0;
                      const canVote =
                        (gameState.phase === 'day' ||
                          gameState.phase === 'voting') &&
                        playerRole.alive &&
                        player.alive &&
                        playerName_key !== playerName;
                      const hasVotedForThis = currentVote === playerName_key;

                      return (
                        <div
                          key={playerName_key || `player-${index}`}
                          className={`p-3 rounded-lg transition-all duration-300 ${
                            player.alive
                              ? 'bg-slate-700/50'
                              : 'bg-slate-900/50 player-eliminated'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <span
                                className={`font-medium ${
                                  player.alive
                                    ? 'text-white'
                                    : 'text-slate-500 line-through'
                                }`}
                                style={{
                                  color: player.alive
                                    ? playerColors[playerName_key] || '#ffffff'
                                    : '#64748b',
                                }}
                              >
                                {playerName_key}
                                {playerName_key === playerName && ' (Vous)'}
                              </span>

                              {/* Compteur de votes */}
                              {voteCount > 0 && (
                                <Badge
                                  variant="destructive"
                                  className="text-xs"
                                >
                                  {voteCount}/{getTotalAlivePlayers()}
                                </Badge>
                              )}
                            </div>

                            <div className="flex items-center space-x-2">
                              {/* Bouton de vote */}
                              {canVote && (
                                <Button
                                  onClick={() => castVote(playerName_key)}
                                  size="sm"
                                  className={`text-xs vote-transition ${
                                    hasVotedForThis
                                      ? 'bg-gray-600 cursor-not-allowed'
                                      : 'bg-slate-600 hover:bg-slate-700'
                                  }`}
                                  disabled={hasVotedForThis}
                                >
                                  {hasVotedForThis ? 'Voté' : 'Voter'}
                                </Button>
                              )}

                              {/* Autres badges */}
                              {gameState.phase === 'voting' &&
                                player.has_voted && (
                                  <Badge
                                    variant="secondary"
                                    className="text-xs vote-cast"
                                  >
                                    A voté
                                  </Badge>
                                )}

                              {!player.alive && (
                                <Badge
                                  variant="destructive"
                                  className="text-xs"
                                >
                                  Éliminé
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* 🆕 Panel de Procès */}
      {showTrialPanel && gameState?.phase === 'trial' && (
        <TrialPanel
          gameState={gameState}
          playerName={playerName}
          onTrialVote={handleTrialVote}
          trialInfo={trialInfo}
        />
      )}
    </div>
  );
}

export default GameRoom;
