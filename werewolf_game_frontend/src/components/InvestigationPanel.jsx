import React, { useState, useEffect } from 'react';
import { Eye, Search, FileText, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import { getInvestigationResults } from '../services/api';

const InvestigationPanel = ({ 
  gameId, 
  playerName, 
  playerRole, 
  isVisible, 
  onClose 
}) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Charger les résultats d'investigation
  useEffect(() => {
    if (isVisible && playerName && (playerRole === 'sheriff' || playerRole === 'investigator')) {
      loadInvestigationResults();
    }
  }, [isVisible, playerName, playerRole]);

  const loadInvestigationResults = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getInvestigationResults(gameId, playerName);
      if (response.success) {
        setResults(response.results || []);
      } else {
        setError(response.message || 'Erreur de chargement');
      }
    } catch (err) {
      setError('Erreur de connexion');
      console.error('Erreur chargement investigations:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = () => {
    return playerRole === 'sheriff' ? <Search className="w-5 h-5" /> : <Eye className="w-5 h-5" />;
  };

  const getRoleTitle = () => {
    return playerRole === 'sheriff' ? 'DOSSIER SHERIFF' : 'RAPPORT INVESTIGATEUR';
  };

  const getResultIcon = (result) => {
    if (playerRole === 'sheriff') {
      return result === 'suspicious' ? 
        <AlertTriangle className="w-4 h-4 text-red-400" /> : 
        <CheckCircle className="w-4 h-4 text-green-400" />;
    }
    return <FileText className="w-4 h-4 text-blue-400" />;
  };

  const formatResult = (resultData) => {
    if (playerRole === 'sheriff') {
      return resultData.result === 'suspicious' ? 'SUSPECT' : 'NON SUSPECT';
    }
    return resultData.result_message || 'Résultat indisponible';
  };

  const getResultClass = (result) => {
    if (playerRole === 'sheriff') {
      return result === 'suspicious' ? 
        'text-red-400 font-bold' : 
        'text-green-400 font-bold';
    }
    return 'text-blue-400';
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="investigation-panel bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        
        {/* Header */}
        <div className="investigation-header p-6 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getRoleIcon()}
              <h2 className="text-xl font-bold text-white">{getRoleTitle()}</h2>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
          <p className="text-slate-300 mt-2 text-sm">
            {playerRole === 'sheriff' ? 
              'Vos enquêtes pour déterminer la culpabilité des suspects' :
              'Vos analyses pour identifier les types de rôles'
            }
          </p>
        </div>

        {/* Content */}
        <div className="investigation-content p-6 max-h-[400px] overflow-y-auto">
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
              <p className="text-slate-400 mt-2">Chargement des données...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-8">
              <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-2" />
              <p className="text-red-400">{error}</p>
              <button
                onClick={loadInvestigationResults}
                className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Réessayer
              </button>
            </div>
          )}

          {!loading && !error && results.length === 0 && (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-slate-500 mx-auto mb-2" />
              <p className="text-slate-400">Aucune investigation effectuée</p>
              <p className="text-slate-500 text-sm mt-1">
                Vos résultats d'enquête apparaîtront ici
              </p>
            </div>
          )}

          {!loading && !error && results.length > 0 && (
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={index}
                  className="investigation-result bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getResultIcon(result.result)}
                      <span className="font-semibold text-white">
                        Investigation #{results.length - index}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-slate-400 text-sm">
                      <Clock className="w-3 h-3" />
                      Nuit {result.night}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Cible</p>
                      <p className="text-white font-medium">{result.target}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-1">Résultat</p>
                      <p className={`font-medium ${getResultClass(result.result)}`}>
                        {formatResult(result)}
                      </p>
                    </div>
                  </div>

                  {result.result_message && playerRole === 'investigator' && (
                    <div className="mt-3 p-3 bg-slate-900/50 rounded border border-slate-600">
                      <p className="text-slate-300 text-sm">
                        {result.result_message}
                      </p>
                    </div>
                  )}

                  <div className="mt-3 text-xs text-slate-500">
                    {new Date(result.timestamp).toLocaleString('fr-FR')}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="investigation-footer p-4 bg-slate-800/50 border-t border-slate-700">
          <div className="flex items-center justify-between text-sm">
            <div className="text-slate-400">
              {results.length} investigation{results.length !== 1 ? 's' : ''} effectuée{results.length !== 1 ? 's' : ''}
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestigationPanel;