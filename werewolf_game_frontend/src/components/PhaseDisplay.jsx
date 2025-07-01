import React, { useState, useEffect } from 'react';
import { Moon, Sun, Gavel, Users, Clock, AlertTriangle } from 'lucide-react';

// Configuration des phases avec couleurs et animations
const PHASE_CONFIG = {
  lobby: {
    name: 'Salon',
    icon: Users,
    background: 'from-blue-900 via-purple-900 to-indigo-900',
    textColor: 'text-blue-100',
    animation: 'lobbyPulse',
    description: 'En attente des joueurs'
  },
  night: {
    name: 'Nuit',
    icon: Moon,
    background: 'from-gray-900 via-purple-900 to-black',
    textColor: 'text-purple-100',
    animation: 'nightShimmer',
    description: 'Les forces du mal s\'agitent...'
  },
  day: {
    name: 'Jour',
    icon: Sun,
    background: 'from-yellow-600 via-orange-600 to-red-600',
    textColor: 'text-yellow-100',
    animation: 'dayRadiance',
    description: 'Le village se réunit pour délibérer'
  },
  voting: {
    name: 'Vote',
    icon: Gavel,
    background: 'from-amber-700 via-orange-700 to-red-700',
    textColor: 'text-amber-100',
    animation: 'votingTension',
    description: 'Choisissez qui accuser !'
  },
  trial: {
    name: 'Procès',
    icon: AlertTriangle,
    background: 'from-red-900 via-amber-900 to-yellow-900',
    textColor: 'text-red-100',
    animation: 'trialDrama',
    description: 'Le destin de l\'accusé se joue'
  },
  lynching: {
    name: 'Exécution',
    icon: AlertTriangle,
    background: 'from-red-950 via-black to-gray-900',
    textColor: 'text-red-200',
    animation: 'executionSolemnity',
    description: 'Justice sera rendue...'
  }
};

const PhaseDisplay = ({ 
  currentPhase, 
  timeRemaining, 
  totalTime,
  showTransition = false,
  transitionText = '',
  dayNumber = 1
}) => {
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [previousPhase, setPreviousPhase] = useState(null);

  // Gérer les transitions de phase
  useEffect(() => {
    if (showTransition && previousPhase !== currentPhase) {
      setIsTransitioning(true);
      setPreviousPhase(currentPhase);
      
      // Fin de transition après 3 secondes
      const timer = setTimeout(() => {
        setIsTransitioning(false);
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [currentPhase, showTransition, previousPhase]);

  const phaseConfig = PHASE_CONFIG[currentPhase] || PHASE_CONFIG.lobby;
  const PhaseIcon = phaseConfig.icon;

  // Calculer le pourcentage de temps restant
  const progress = totalTime > 0 ? ((totalTime - timeRemaining) / totalTime) * 100 : 0;
  const isTimerCritical = timeRemaining <= 10 && timeRemaining > 0;

  // Format du temps (mm:ss)
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Animation de transition
  if (isTransitioning) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center phase-transition-overlay">
        <div className={`absolute inset-0 bg-gradient-to-br ${phaseConfig.background} opacity-95`} />
        <div className="relative z-10 text-center transition-animation">
          <div className="mb-4">
            <PhaseIcon className={`w-24 h-24 mx-auto ${phaseConfig.textColor} transition-icon`} />
          </div>
          <h1 className={`text-6xl font-bold ${phaseConfig.textColor} mb-4 transition-title`}>
            {transitionText || phaseConfig.name.toUpperCase()}
          </h1>
          {dayNumber > 1 && currentPhase === 'day' && (
            <p className={`text-2xl ${phaseConfig.textColor} opacity-80 transition-subtitle`}>
              Jour {dayNumber}
            </p>
          )}
          <p className={`text-xl ${phaseConfig.textColor} opacity-70 mt-4 transition-description`}>
            {phaseConfig.description}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`phase-display bg-gradient-to-r ${phaseConfig.background} border-b-4 border-black/30 shadow-2xl`}>
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          
          {/* Phase actuelle */}
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-full bg-black/20 ${phaseConfig.animation}`}>
              <PhaseIcon className={`w-6 h-6 ${phaseConfig.textColor}`} />
            </div>
            <div>
              <h2 className={`text-xl font-bold ${phaseConfig.textColor}`}>
                {phaseConfig.name}
                {dayNumber > 1 && currentPhase === 'day' && (
                  <span className="ml-2 opacity-80">- Jour {dayNumber}</span>
                )}
              </h2>
              <p className={`text-sm ${phaseConfig.textColor} opacity-70`}>
                {phaseConfig.description}
              </p>
            </div>
          </div>

          {/* Timer et progression */}
          {timeRemaining > 0 && (
            <div className="flex items-center space-x-4">
              
              {/* Barre de progression */}
              <div className="w-32 h-2 bg-black/30 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-1000 ${
                    isTimerCritical 
                      ? 'bg-red-400 timer-critical' 
                      : 'bg-white/60'
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>

              {/* Temps restant */}
              <div className="flex items-center space-x-2">
                <Clock className={`w-4 h-4 ${phaseConfig.textColor} ${isTimerCritical ? 'timer-critical' : ''}`} />
                <span className={`text-lg font-mono font-bold ${phaseConfig.textColor} ${isTimerCritical ? 'timer-critical text-red-200' : ''}`}>
                  {formatTime(timeRemaining)}
                </span>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default PhaseDisplay;