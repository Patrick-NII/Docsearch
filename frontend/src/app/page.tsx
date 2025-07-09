'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import { LoginForm } from '../components/LoginForm';
import { RegisterForm } from '../components/RegisterForm';
import { UserProfile } from '../components/UserProfile';
import { ProtectedRoute } from '../components/ProtectedRoute';
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
  const { user, isAuthenticated, isLoading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);
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

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Charger les données au démarrage si authentifié
  useEffect(() => {
    if (isAuthenticated) {
      loadAvailableDocuments();
      loadChatHistory();
    }
  }, [isAuthenticated]);

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
      const response = await axios.post(`${API_URL}/upload`, formData);
      
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
        { question }
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
      const response = await axios.get(`${API_URL}/documents`);
      setAvailableDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Erreur lors du chargement des documents:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/history`);
      
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
      await axios.delete(`${API_URL}/session`);
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
      await axios.delete(`${API_URL}/history`);
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
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Afficher les formulaires d'authentification si non connecté
  if (!isAuthenticated && !isLoading) {
    return showRegister ? (
      <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
    );
  }

  // Afficher le chargement
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  // Interface principale (utilisateur authentifié)
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">
                  DocSearch AI
                </h1>
                {user?.is_admin && (
                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                    Admin
                  </span>
                )}
              </div>
              <UserProfile />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Upload de Documents
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sélectionner un fichier
                    </label>
                    <input
                      type="file"
                      onChange={handleFileChange}
                      accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                    />
                  </div>

                  <button
                    onClick={handleUpload}
                    disabled={!file || loading}
                    className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Upload...' : 'Uploader'}
                  </button>

                  {uploadStatus && (
                    <div className="text-sm text-gray-600">
                      {uploadStatus}
                    </div>
                  )}

                  {sessionId && (
                    <button
                      onClick={clearCurrentSession}
                      className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
                    >
                      Effacer la session
                    </button>
                  )}
                </div>

                <div className="mt-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">
                    Documents disponibles
                  </h3>
                  <div className="space-y-2">
                    {availableDocuments.map((doc, index) => (
                      <div key={index} className="text-xs text-gray-600 p-2 bg-gray-50 rounded">
                        <div className="font-medium">{doc.filename}</div>
                        <div>{doc.file_type} • {doc.chunks_count} segments</div>
                        {doc.session_id && (
                          <div className="text-indigo-600">Session actuelle</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Area */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow">
                {/* Chat Header */}
                <div className="border-b border-gray-200 p-4">
                  <div className="flex justify-between items-center">
                    <h2 className="text-lg font-medium text-gray-900">
                      Assistant IA
                    </h2>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setShowHistory(!showHistory)}
                        className="text-sm text-indigo-600 hover:text-indigo-500"
                      >
                        {showHistory ? 'Masquer' : 'Afficher'} l'historique
                      </button>
                      <button
                        onClick={clearConversationHistory}
                        className="text-sm text-red-600 hover:text-red-500"
                      >
                        Effacer l'historique
                      </button>
                    </div>
                  </div>
                </div>

                {/* Chat Messages */}
                <div className="h-96 overflow-y-auto p-4">
                  {showHistory && conversationHistory.length > 0 && (
                    <div className="space-y-4 mb-4">
                      {conversationHistory.map((entry) => (
                        <div key={entry.id} className="space-y-2">
                          <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                              <span className="text-indigo-600 text-sm font-medium">U</span>
                            </div>
                            <div className="flex-1">
                              <div className="bg-gray-100 rounded-lg p-3">
                                <p className="text-sm text-gray-900">{entry.question}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {formatTimestamp(entry.timestamp)}
                                </p>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <span className="text-green-600 text-sm font-medium">AI</span>
                            </div>
                            <div className="flex-1">
                              <div className="bg-green-50 rounded-lg p-3">
                                <p className="text-sm text-gray-900 whitespace-pre-wrap">{entry.answer}</p>
                                {entry.sources && entry.sources.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-gray-500 font-medium">Sources :</p>
                                    <div className="space-y-1">
                                      {entry.sources.map((source, idx) => (
                                        <div key={idx} className="text-xs text-gray-600 bg-white p-2 rounded">
                                          <div className="font-medium">{source.filename}</div>
                                          <div className="text-gray-500">{source.text.substring(0, 100)}...</div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Current Answer */}
                  {answer && (
                    <div className="space-y-2">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                          <span className="text-green-600 text-sm font-medium">AI</span>
                        </div>
                        <div className="flex-1">
                          <div className="bg-green-50 rounded-lg p-3">
                            <p className="text-sm text-gray-900 whitespace-pre-wrap">{answer}</p>
                            {sources && sources.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs text-gray-500 font-medium">Sources :</p>
                                <div className="space-y-1">
                                  {sources.map((source, idx) => (
                                    <div key={idx} className="text-xs text-gray-600 bg-white p-2 rounded">
                                      <div className="font-medium">{source.filename}</div>
                                      <div className="text-gray-500">{source.text.substring(0, 100)}...</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {loading && (
                    <div className="flex items-center space-x-2 text-gray-500">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                      <span className="text-sm">L'assistant réfléchit...</span>
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-200 p-4">
                  <div className="flex space-x-4">
                    <div className="flex-1">
                      <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Posez votre question ici..."
                        className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                        rows={3}
                      />
                    </div>
                    <button
                      onClick={handleAsk}
                      disabled={!question.trim() || loading}
                      className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Envoyer
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
