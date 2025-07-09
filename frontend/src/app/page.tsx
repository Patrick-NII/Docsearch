'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface ConversationEntry {
  id: string;
  question: string;
  answer: string;
  sources: any[];
  timestamp: Date;
  context: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [context, setContext] = useState('');
  const [availableDocuments, setAvailableDocuments] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<ConversationEntry[]>([]);
  const [showHistory, setShowHistory] = useState(true);

  const API_URL = 'http://localhost:8000';
  const API_TOKEN = 'dev-secret-token'; // À synchroniser avec ton .env backend

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadStatus('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Veuillez sélectionner un fichier');
      return;
    }

    setLoading(true);
    setUploadStatus('Upload en cours...');
    
    const formData = new FormData();
    formData.append('files', file);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setUploadStatus(`✅ ${response.data.documents_processed} document(s) traité(s) avec succès`);
      setAnswer('');
      setSources([]);
      setContext('current_session');
      setSessionId(response.data.session_id);
      
      // Charger la liste des documents disponibles
      loadAvailableDocuments();
    } catch (error: any) {
      console.error('Erreur upload:', error);
      setUploadStatus(`❌ Erreur: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) {
      alert('Veuillez poser une question');
      return;
    }

    setLoading(true);
    setAnswer('');
    setSources([]);

    try {
      const response = await axios.post(
        `${API_URL}/ask`,
        { question },
        {
          headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const newAnswer = response.data.answer;
      const newSources = response.data.sources || [];
      const newContext = response.data.context || '';

      setAnswer(newAnswer);
      setSources(newSources);
      setContext(newContext);

      // Ajouter à l'historique
      const newEntry: ConversationEntry = {
        id: Date.now().toString(),
        question: question,
        answer: newAnswer,
        sources: newSources,
        timestamp: new Date(),
        context: newContext
      };

      setConversationHistory(prev => [newEntry, ...prev]);
      setQuestion(''); // Vider la question après envoi
    } catch (error: any) {
      console.error('Erreur question:', error);
      const errorMessage = `❌ Erreur: ${error.response?.data?.detail || error.message}`;
      setAnswer(errorMessage);
      
      // Ajouter l'erreur à l'historique aussi
      const errorEntry: ConversationEntry = {
        id: Date.now().toString(),
        question: question,
        answer: errorMessage,
        sources: [],
        timestamp: new Date(),
        context: 'error'
      };
      setConversationHistory(prev => [errorEntry, ...prev]);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/documents`, {
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
        },
      });
      setAvailableDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Erreur lors du chargement des documents:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/history`, {
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
        },
      });
      
      // Convertir l'historique du backend en format frontend
      const backendHistory = response.data.history || [];
      const convertedHistory: ConversationEntry[] = backendHistory.map((entry: any, index: number) => ({
        id: `backend-${index}`,
        question: entry.question || '',
        answer: entry.answer || '',
        sources: [], // Le backend ne stocke pas les sources dans l'historique
        timestamp: new Date(), // Le backend ne stocke pas le timestamp
        context: 'backend_history'
      }));
      
      setConversationHistory(convertedHistory);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique:', error);
    }
  };

  const clearCurrentSession = async () => {
    try {
      await axios.delete(`${API_URL}/session`, {
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
        },
      });
      setSessionId(null);
      setContext('');
      setAnswer('');
      setSources([]);
      setUploadStatus('Session actuelle effacée');
      loadAvailableDocuments();
    } catch (error: any) {
      console.error('Erreur lors de l\'effacement de la session:', error);
    }
  };

  const clearConversationHistory = async () => {
    try {
      await axios.delete(`${API_URL}/history`, {
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
        },
      });
      setConversationHistory([]);
      setAnswer('');
      setSources([]);
    } catch (error: any) {
      console.error('Erreur lors de l\'effacement de l\'historique:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Charger les documents et l'historique au démarrage
  useEffect(() => {
    loadAvailableDocuments();
    loadChatHistory();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🧠 DocSearch AI
          </h1>
          <p className="text-gray-600 mb-6">
            Assistant IA pour analyser vos documents et répondre à vos questions
          </p>

          {/* Indicateur de contexte */}
          {context && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-medium text-blue-900">
                    📋 Contexte actuel: 
                  </span>
                  <span className="ml-2 text-blue-700">
                    {context === 'current_session' ? 'Document uploadé récemment' : 
                     context === 'all_documents' ? 'Tous les documents en base' : 
                     context === 'document_listing' ? 'Liste des documents' : context}
                  </span>
                </div>
                <div className="flex gap-2">
                  {sessionId && (
                    <button
                      onClick={clearCurrentSession}
                      className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
                    >
                      🗑️ Effacer session
                    </button>
                  )}
                  <button
                    onClick={() => setShowHistory(!showHistory)}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
                  >
                    {showHistory ? '📝 Masquer historique' : '📝 Afficher historique'}
                  </button>
                  {conversationHistory.length > 0 && (
                    <button
                      onClick={clearConversationHistory}
                      className="px-3 py-1 bg-orange-100 text-orange-700 rounded text-sm hover:bg-orange-200"
                    >
                      🗑️ Effacer historique
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Section Upload */}
          <div className="mb-8 p-4 border border-gray-200 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">📄 Upload de Document</h2>
            <div className="flex items-center gap-4">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.txt,.docx,.doc,.xlsx,.xls,.csv,.png,.jpg,.jpeg,.gif,.bmp,.tiff"
                className="flex-1 p-2 border border-gray-300 rounded"
              />
              <button
                onClick={handleUpload}
                disabled={loading || !file}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? '⏳ Upload...' : '📤 Uploader'}
              </button>
            </div>
            {uploadStatus && (
              <p className={`mt-2 text-sm ${uploadStatus.includes('✅') ? 'text-green-600' : 'text-red-600'}`}>
                {uploadStatus}
              </p>
            )}
          </div>

          {/* Section Documents Disponibles */}
          {availableDocuments.length > 0 && (
            <div className="mb-8 p-4 border border-gray-200 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">📚 Documents Disponibles</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {availableDocuments.map((doc, index) => (
                  <div key={index} className="bg-gray-50 p-3 rounded border">
                    <div className="font-medium text-gray-900">
                      📄 {doc.filename}
                    </div>
                    <div className="text-sm text-gray-600">
                      Type: {doc.file_type} • Segments: {doc.chunks_count}
                    </div>
                    <div className="text-xs text-gray-500">
                      {doc.session_id === 'Permanent' ? '📚 Permanent' : '📄 Session actuelle'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section Question */}
          <div className="mb-8 p-4 border border-gray-200 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">🤔 Poser une Question</h2>
            <div className="flex gap-4">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Posez votre question sur le document..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleAsk}
                disabled={loading || !question.trim()}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? '⏳ Recherche...' : '🔍 Demander'}
              </button>
            </div>
          </div>

          {/* Section Historique des Conversations */}
          {showHistory && conversationHistory.length > 0 && (
            <div className="mb-8 p-4 border border-gray-200 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">💬 Historique des Conversations</h2>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {conversationHistory.map((entry) => (
                  <div key={entry.id} className="bg-gray-50 p-4 rounded-lg border">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">
                          {formatTimestamp(entry.timestamp)}
                        </span>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {entry.context === 'current_session' ? 'Session' : 
                           entry.context === 'all_documents' ? 'Tous' : 
                           entry.context === 'document_listing' ? 'Liste' : entry.context}
                        </span>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="font-medium text-gray-900 mb-1">
                        🤔 Question:
                      </div>
                      <div className="text-gray-700 bg-white p-2 rounded border">
                        {entry.question}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="font-medium text-gray-900 mb-1">
                        💬 Réponse:
                      </div>
                      <div className="text-gray-700 bg-white p-2 rounded border whitespace-pre-wrap">
                        {entry.answer}
                      </div>
                    </div>

                    {/* Sources */}
                    {entry.sources && entry.sources.length > 0 && (
                      <div>
                        <div className="font-medium text-gray-900 mb-2">
                          📚 Sources ({entry.sources.length}):
                        </div>
                        <div className="space-y-2">
                          {entry.sources.map((source, index) => (
                            <div key={index} className="bg-blue-50 p-2 rounded border-l-2 border-blue-400">
                              <div className="text-sm font-medium text-blue-900">
                                📄 {source.filename} ({source.file_type})
                              </div>
                              <div className="text-xs text-blue-700 mt-1">
                                {source.text?.slice(0, 150)}...
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section Réponse Actuelle (si pas d'historique affiché) */}
          {answer && !showHistory && (
            <div className="p-4 border border-gray-200 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">💬 Réponse</h2>
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <p className="text-gray-800 whitespace-pre-wrap">{answer}</p>
              </div>

              {/* Sources */}
              {sources.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">📚 Sources</h3>
                  <div className="space-y-2">
                    {sources.map((source, index) => (
                      <div key={index} className="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-400">
                        <div className="font-medium text-blue-900">
                          📄 {source.filename} ({source.file_type})
                        </div>
                        <div className="text-sm text-blue-700 mt-1">
                          {source.text?.slice(0, 200)}...
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">📋 Instructions</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Upload un document pour créer une session de travail</li>
            <li>• Posez une question en langage naturel</li>
            <li>• L'IA utilisera automatiquement le document uploadé</li>
            <li>• L'historique des conversations est conservé en mémoire</li>
            <li>• Demandez "quels documents sont disponibles ?" pour voir la base</li>
            <li>• Appuyez sur Entrée pour poser la question</li>
            <li>• Utilisez "Effacer session" pour supprimer les documents récents</li>
            <li>• Utilisez "Effacer historique" pour supprimer la mémoire conversationnelle</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
