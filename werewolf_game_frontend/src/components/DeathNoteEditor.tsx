import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skull, PenTool, Target, Send } from 'lucide-react';
import { Alert, AlertDescription } from "@/components/ui/alert";

interface DeathNoteEditorProps {
  gameId: string;
  playerName: string;
  isAlive: boolean;
  canLeaveNotes: boolean;
  className?: string;
}

interface Target {
  name: string;
  role: string;
}

export const DeathNoteEditor: React.FC<DeathNoteEditorProps> = ({
  gameId,
  playerName,
  isAlive,
  canLeaveNotes,
  className = ""
}) => {
  const [noteContent, setNoteContent] = useState('');
  const [selectedTarget, setSelectedTarget] = useState('');
  const [availableTargets, setAvailableTargets] = useState<Target[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  // Charger les cibles disponibles
  useEffect(() => {
    const loadTargets = async () => {
      if (!canLeaveNotes) return;
      
      try {
        const response = await fetch(`/api/games/${gameId}/death-note-targets?player_name=${playerName}`);
        if (response.ok) {
          const data = await response.json();
          setAvailableTargets(data.targets || []);
        }
      } catch (error) {
        console.error('Erreur lors du chargement des cibles:', error);
      }
    };

    loadTargets();
  }, [gameId, playerName, canLeaveNotes]);

  const saveDeathNote = async () => {
    if (!selectedTarget || !noteContent.trim()) {
      setMessage('⚠️ Sélectionnez une cible et écrivez une note');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch(`/api/games/${gameId}/death-note`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          killer_name: playerName,
          victim_name: selectedTarget,
          death_note: noteContent
        }),
      });

      const result = await response.json();

      if (result.success) {
        setMessage(`🩸 Note de mort préparée pour ${selectedTarget}`);
        setNoteContent('');
        setSelectedTarget('');
      } else {
        setMessage(`❌ Erreur: ${result.error}`);
      }
    } catch (error) {
      setMessage('❌ Erreur de connexion');
      console.error('Erreur sauvegarde note de mort:', error);
    }

    setIsLoading(false);
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  if (!canLeaveNotes) {
    return null; // Ne pas afficher le composant si le joueur ne peut pas laisser de notes
  }

  return (
    <Card className={`death-note-editor ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-red-700 dark:text-red-400">
          <div className="flex items-center gap-2">
            <Skull className="h-5 w-5" />
            <span>Notes de Mort</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleExpanded}
            className="text-red-600 hover:text-red-700"
          >
            <PenTool className="h-4 w-4" />
            {isExpanded ? 'Masquer' : 'Écrire'}
          </Button>
        </CardTitle>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          <Alert className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/20">
            <AlertDescription className="text-sm text-red-800 dark:text-red-200">
              🩸 Laissez un message qui sera révélé sur le corps de votre victime...
            </AlertDescription>
          </Alert>

          <div className="space-y-3">
            <div className="target-selection">
              <label className="text-sm font-medium text-red-700 dark:text-red-300 mb-2 block">
                <Target className="h-4 w-4 inline mr-1" />
                Cible sélectionnée
              </label>
              <Select value={selectedTarget} onValueChange={setSelectedTarget}>
                <SelectTrigger className="bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-950/20 dark:to-rose-950/20 border-red-200 dark:border-red-800">
                  <SelectValue placeholder="Choisissez votre prochaine victime..." />
                </SelectTrigger>
                <SelectContent>
                  {availableTargets.map((target) => (
                    <SelectItem key={target.name} value={target.name}>
                      {target.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="note-editor">
              <label className="text-sm font-medium text-red-700 dark:text-red-300 mb-2 block">
                <Skull className="h-4 w-4 inline mr-1" />
                Votre message de mort
              </label>
              <Textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                placeholder="Laissez un message sinistre... Une menace, un indice, une confession..."
                disabled={!isAlive || isLoading}
                rows={4}
                maxLength={300}
                className="death-note-textarea font-mono bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-950/20 dark:to-rose-950/20 border-red-200 dark:border-red-800 focus:border-red-400 focus:ring-red-400/20 text-red-900 dark:text-red-100"
              />
              
              <div className="flex justify-between items-center mt-2">
                <div className="text-xs text-muted-foreground">
                  {noteContent.length}/300 caractères
                </div>
                
                <Button
                  onClick={saveDeathNote}
                  disabled={isLoading || !selectedTarget || !noteContent.trim()}
                  size="sm"
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  <Send className="h-4 w-4 mr-1" />
                  {isLoading ? 'Préparation...' : 'Préparer Note'}
                </Button>
              </div>
            </div>

            {message && (
              <Alert className={message.includes('❌') ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}>
                <AlertDescription className="text-sm">
                  {message}
                </AlertDescription>
              </Alert>
            )}

            <div className="death-note-preview p-4 bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-950/10 dark:to-rose-950/10 rounded-lg border border-red-200 dark:border-red-800">
              <h4 className="font-semibold text-red-800 dark:text-red-300 mb-2">
                🩸 Aperçu de la note
              </h4>
              <div className="death-note-content font-mono text-sm text-red-900 dark:text-red-200 whitespace-pre-wrap">
                {noteContent || (
                  <em className="text-muted-foreground">
                    {selectedTarget 
                      ? `Votre message sera trouvé sur le corps de ${selectedTarget}...`
                      : 'Sélectionnez une cible et écrivez votre message...'
                    }
                  </em>
                )}
              </div>
            </div>

            {!isAlive && (
              <Alert className="border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900">
                <AlertDescription className="text-sm text-muted-foreground">
                  💀 Vous ne pouvez plus laisser de notes de mort car vous êtes mort.
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
};