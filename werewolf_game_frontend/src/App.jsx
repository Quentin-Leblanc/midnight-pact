import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Label } from '@/components/ui/label.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Users, Play, Plus, LogIn } from 'lucide-react';
import GameRoom from './GameRoom.jsx';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [games, setGames] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showJoinForm, setShowJoinForm] = useState(false);
  const [selectedGame, setSelectedGame] = useState(null);
  const [playerName, setPlayerName] = useState('');
  const [newGameName, setNewGameName] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(10);
  const [roomCode, setRoomCode] = useState('');
  const [currentRoom, setCurrentRoom] = useState(null);
  const [currentPlayer, setCurrentPlayer] = useState('');

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/games`);
      const data = await response.json();
      setGames(data);
    } catch (error) {
      console.error('Error fetching games:', error);
    }
  };

  const createGame = async () => {
    if (!newGameName.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/games`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newGameName,
          max_players: maxPlayers,
        }),
      });

      if (response.ok) {
        const newGame = await response.json();
        setGames([...games, newGame]);
        setNewGameName('');
        setMaxPlayers(10);
        setShowCreateForm(false);
      }
    } catch (error) {
      console.error('Error creating game:', error);
    }
  };

  const joinGame = async (gameRoomCode) => {
    if (!playerName.trim()) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/games/${gameRoomCode}/join`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            player_name: playerName,
          }),
        }
      );

      if (response.ok) {
        // Successfully joined, enter game room
        setCurrentRoom(gameRoomCode);
        setCurrentPlayer(playerName);
        setShowJoinForm(false);
        setPlayerName('');
        setRoomCode('');
      } else {
        const error = await response.json();
        alert(error.error);
      }
    } catch (error) {
      console.error('Error joining game:', error);
    }
  };

  const leaveGame = async () => {
    if (currentRoom && currentPlayer) {
      try {
        await fetch(`${API_BASE_URL}/games/${currentRoom}/leave`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            player_name: currentPlayer,
          }),
        });
      } catch (error) {
        console.error('Error leaving game:', error);
      }
    }

    setCurrentRoom(null);
    setCurrentPlayer('');
    fetchGames(); // Refresh games list
  };

  // If in a game room, show the game interface
  if (currentRoom && currentPlayer) {
    return (
      <GameRoom
        roomCode={currentRoom}
        playerName={currentPlayer}
        onLeaveGame={leaveGame}
      />
    );
  }

  // Otherwise show the lobby
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Loup-Garou Online
          </h1>
          <p className="text-blue-200">
            Rejoignez une partie multijoueur inspirée de SC2 Mafia
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-4 mb-8">
          <Button
            onClick={() => setShowCreateForm(true)}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Créer une Partie
          </Button>
          <Button
            onClick={() => setShowJoinForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <LogIn className="w-4 h-4 mr-2" />
            Rejoindre par Code
          </Button>
        </div>

        {/* Create Game Form */}
        {showCreateForm && (
          <Card className="mb-6 bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">
                Créer une Nouvelle Partie
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="gameName" className="text-white">
                  Nom de la Partie
                </Label>
                <Input
                  id="gameName"
                  value={newGameName}
                  onChange={(e) => setNewGameName(e.target.value)}
                  placeholder="Entrez le nom de la partie"
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div>
                <Label htmlFor="maxPlayers" className="text-white">
                  Nombre Maximum de Joueurs
                </Label>
                <Input
                  id="maxPlayers"
                  type="number"
                  min="4"
                  max="20"
                  value={maxPlayers}
                  onChange={(e) => setMaxPlayers(parseInt(e.target.value))}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={createGame}
                  className="bg-green-600 hover:bg-green-700"
                >
                  Créer
                </Button>
                <Button
                  onClick={() => setShowCreateForm(false)}
                  variant="outline"
                  className="border-slate-600 text-slate-200 bg-slate-700 hover:bg-slate-600 hover:text-white"
                >
                  Annuler
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Join by Code Form */}
        {showJoinForm && (
          <Card className="mb-6 bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Rejoindre une Partie</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="playerName" className="text-white">
                  Votre Nom
                </Label>
                <Input
                  id="playerName"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  placeholder="Entrez votre nom"
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div>
                <Label htmlFor="roomCode" className="text-white">
                  Code de la Salle
                </Label>
                <Input
                  id="roomCode"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value)}
                  placeholder="Entrez le code de la salle"
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => joinGame(roomCode)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Rejoindre
                </Button>
                <Button
                  onClick={() => setShowJoinForm(false)}
                  variant="outline"
                  className="border-slate-600 text-slate-200 bg-slate-700 hover:bg-slate-600 hover:text-white"
                >
                  Annuler
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Games List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {games.map((game) => (
            <Card
              key={game.id}
              className="bg-slate-800 border-slate-700 hover:bg-slate-750 transition-colors"
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-white text-lg">
                      {game.name}
                    </CardTitle>
                    <CardDescription className="text-slate-400">
                      Code: {game.room_code}
                    </CardDescription>
                  </div>
                  <Badge
                    variant={
                      game.status === 'waiting' ? 'default' : 'secondary'
                    }
                    className={
                      game.status === 'waiting'
                        ? 'bg-green-600'
                        : 'bg-yellow-600'
                    }
                  >
                    {game.status === 'waiting' ? 'En Attente' : 'En Cours'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-slate-300">
                    <Users className="w-4 h-4 mr-2" />
                    <span>
                      {game.current_players}/{game.max_players}
                    </span>
                  </div>
                  {game.status === 'waiting' && (
                    <Button
                      size="sm"
                      onClick={() => {
                        setRoomCode(game.room_code);
                        setShowJoinForm(true);
                      }}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Rejoindre
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {games.length === 0 && (
          <div className="text-center text-slate-400 mt-8">
            <p>Aucune partie disponible. Créez-en une nouvelle !</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
