const API_BASE_URL = 'http://localhost:5000/api';

// ==================== GAME MANAGEMENT ====================

export const createGame = async (gameData) => {
  const response = await fetch(`${API_BASE_URL}/create-game`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(gameData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create game');
  }
  
  return response.json();
};

export const joinGame = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/join-game/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ player_name: playerName })
  });
  
  if (!response.ok) {
    throw new Error('Failed to join game');
  }
  
  return response.json();
};

export const startGame = async (gameId) => {
  const response = await fetch(`${API_BASE_URL}/start-game/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to start game');
  }
  
  return response.json();
};

export const getGameState = async (gameId) => {
  const response = await fetch(`${API_BASE_URL}/game-state/${gameId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get game state');
  }
  
  return response.json();
};

export const getPlayerRole = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/player-role/${gameId}?player_name=${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get player role');
  }
  
  return response.json();
};

// ==================== GAME ACTIONS ====================

export const performNightAction = async (gameId, actionData) => {
  const response = await fetch(`${API_BASE_URL}/night-action/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(actionData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to perform night action');
  }
  
  return response.json();
};

export const castVote = async (gameId, voteData) => {
  const response = await fetch(`${API_BASE_URL}/vote/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(voteData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to cast vote');
  }
  
  return response.json();
};

export const castTrialVote = async (gameId, voteData) => {
  const response = await fetch(`${API_BASE_URL}/trial-vote/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(voteData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to cast trial vote');
  }
  
  return response.json();
};

export const getTrialInfo = async (gameId) => {
  const response = await fetch(`${API_BASE_URL}/trial-info/${gameId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get trial info');
  }
  
  return response.json();
};

// ==================== CHAT SYSTEM ====================

export const sendChatMessage = async (gameId, messageData) => {
  const response = await fetch(`${API_BASE_URL}/chat/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(messageData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to send chat message');
  }
  
  return response.json();
};

export const getChatMessages = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/chat-messages/${gameId}?player_name=${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get chat messages');
  }
  
  return response.json();
};

export const getChatChannels = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/chat-channels/${gameId}?player_name=${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get chat channels');
  }
  
  return response.json();
};

export const sendPrivateMessage = async (gameId, messageData) => {
  const response = await fetch(`${API_BASE_URL}/private-message/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(messageData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to send private message');
  }
  
  return response.json();
};

// ==================== LAST WILL & DEATH NOTES ====================

export const saveLastWill = async (gameId, willData) => {
  const response = await fetch(`${API_BASE_URL}/save-last-will/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(willData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to save last will');
  }
  
  return response.json();
};

export const getPlayerWill = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/player-will/${gameId}?player_name=${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get player will');
  }
  
  return response.json();
};

export const getRevealedWills = async (gameId) => {
  const response = await fetch(`${API_BASE_URL}/revealed-wills/${gameId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get revealed wills');
  }
  
  return response.json();
};

export const saveDeathNote = async (gameId, deathNoteData) => {
  const response = await fetch(`${API_BASE_URL}/save-death-note/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(deathNoteData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to save death note');
  }
  
  return response.json();
};

export const getDeathNoteTargets = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/death-note-targets/${gameId}?player_name=${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get death note targets');
  }
  
  return response.json();
};

export const getDeathNotesHistory = async (gameId) => {
  const response = await fetch(`${API_BASE_URL}/death-notes-history/${gameId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get death notes history');
  }
  
  return response.json();
};

// 🆕 ==================== CHAPITRE 2 - INVESTIGATION API ====================

// Get investigation results for a player
export const getInvestigationResults = async (gameId, playerName) => {
  const response = await fetch(`${API_BASE_URL}/investigation-results/${gameId}?player_name=${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get investigation results');
  }
  
  return response.json();
};

// Get investigation history for the game
export const getInvestigationHistory = async (gameId) => {
  const response = await fetch(`${API_BASE_URL}/investigation-history/${gameId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get investigation history');
  }
  
  return response.json();
};

// Perform Sheriff investigation
export const performSheriffInvestigation = async (gameId, playerName, targetName) => {
  const response = await fetch(`${API_BASE_URL}/sheriff-investigate/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      player_name: playerName,
      target_name: targetName
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to perform sheriff investigation');
  }
  
  return response.json();
};

// Perform Investigator investigation
export const performInvestigatorInvestigation = async (gameId, playerName, targetName) => {
  const response = await fetch(`${API_BASE_URL}/investigator-investigate/${gameId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      player_name: playerName,
      target_name: targetName
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to perform investigator investigation');
  }
  
  return response.json();
};