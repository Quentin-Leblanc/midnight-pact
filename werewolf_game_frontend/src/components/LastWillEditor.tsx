import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollText, Save, Eye, EyeOff } from 'lucide-react';
import { Alert, AlertDescription } from "@/components/ui/alert";

interface LastWillEditorProps {
  gameId: string;
  playerName: string;
  isAlive: boolean;
  className?: string;
}

interface WillData {
  content: string;
  last_updated: string | null;
  day: number;
}

export const LastWillEditor: React.FC<LastWillEditorProps> = ({
  gameId,
  playerName,
  isAlive,
  className = ""
}) => {
  const [willContent, setWillContent] = useState('');
  const [lastSaved, setLastSaved] = useState<WillData | null>(null);
  const [isLoading, setSLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Charger le testament existant
  useEffect(() => {
    const loadWill = async () => {
      try {
        const response = await fetch(`/api/games/${gameId}/player/${playerName}/will`);
        if (response.ok) {
          const data = await response.json();
          if (data.will) {
            setWillContent(data.will.content || '');
            setLastSaved(data.will);
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement du testament:', error);
      }
    };

    loadWill();
  }, [gameId, playerName]);

  // Détecter les modifications non sauvegardées
  useEffect(() => {
    const savedContent = lastSaved?.content || '';
    setHasUnsavedChanges(willContent !== savedContent);
  }, [willContent, lastSaved]);

  const saveWill = async () => {
    if (!isAlive) {
      setMessage('⚰️ Les morts ne peuvent pas modifier leur testament');
      return;
    }

    setSLoading(true);
    setMessage('');

    try {
      const response = await fetch(`/api/games/${gameId}/player/${playerName}/will`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ will: willContent }),
      });

      const result = await response.json();

      if (result.success) {
        setMessage('📜 Testament sauvegardé');
        setLastSaved({
          content: willContent,
          last_updated: new Date().toISOString(),
          day: lastSaved?.day || 1
        });
        setHasUnsavedChanges(false);
      } else {
        setMessage(`❌ Erreur: ${result.error}`);
      }
    } catch (error) {
      setMessage('❌ Erreur de connexion');
      console.error('Erreur sauvegarde testament:', error);
    }

    setSLoading(false);
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const formatLastUpdated = (timestamp: string | null) => {
    if (!timestamp) return 'Jamais sauvé';
    const date = new Date(timestamp);
    return `${date.toLocaleDateString()} à ${date.toLocaleTimeString()}`;
  };

  return (
    <Card className={`last-will-editor ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-amber-700 dark:text-amber-400">
          <div className="flex items-center gap-2">
            <ScrollText className="h-5 w-5" />
            <span>Testament de {playerName}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleExpanded}
            className="text-amber-600 hover:text-amber-700"
          >
            {isExpanded ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {isExpanded ? 'Réduire' : 'Éditer'}
          </Button>
        </CardTitle>
        
        {lastSaved && (
          <div className="text-sm text-muted-foreground">
            Dernière modification: {formatLastUpdated(lastSaved.last_updated)}
          </div>
        )}
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          <div className="will-editor-container">
            <Textarea
              value={willContent}
              onChange={(e) => setWillContent(e.target.value)}
              placeholder={isAlive 
                ? "Écrivez votre testament... Vos derniers mots, vos suspicions, vos alliances secrètes..." 
                : "Votre testament est figé dans l'éternité..."
              }
              disabled={!isAlive || isLoading}
              rows={6}
              maxLength={1000}
              className="will-textarea font-serif bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20 border-amber-200 dark:border-amber-800 focus:border-amber-400 focus:ring-amber-400/20"
            />
            
            <div className="flex justify-between items-center mt-2">
              <div className="text-xs text-muted-foreground">
                {willContent.length}/1000 caractères
                {hasUnsavedChanges && (
                  <span className="text-amber-600 ml-2">• Modifications non sauvées</span>
                )}
              </div>
              
              {isAlive && (
                <Button
                  onClick={saveWill}
                  disabled={isLoading || !willContent.trim() || !hasUnsavedChanges}
                  size="sm"
                  className="bg-amber-600 hover:bg-amber-700 text-white"
                >
                  <Save className="h-4 w-4 mr-1" />
                  {isLoading ? 'Sauvegarde...' : 'Sauvegarder'}
                </Button>
              )}
            </div>
          </div>

          {message && (
            <Alert className={message.includes('❌') ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}>
              <AlertDescription className="text-sm">
                {message}
              </AlertDescription>
            </Alert>
          )}

          {!isAlive && (
            <Alert className="border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900">
              <AlertDescription className="text-sm text-muted-foreground">
                ⚰️ Votre testament est maintenant figé. Il sera révélé automatiquement lors de votre mort.
              </AlertDescription>
            </Alert>
          )}

          <div className="will-preview p-4 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/10 dark:to-orange-950/10 rounded-lg border border-amber-200 dark:border-amber-800">
            <h4 className="font-semibold text-amber-800 dark:text-amber-300 mb-2">
              📜 Aperçu du testament
            </h4>
            <div className="will-content font-serif text-sm whitespace-pre-wrap">
              {willContent || <em className="text-muted-foreground">Votre testament apparaîtra ici...</em>}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
};