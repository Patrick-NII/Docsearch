'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardContent } from '../components/ui/Card';
import DocumentCard from '../components/DocumentCard';
import ChatMessage from '../components/ChatMessage';
import DocumentViewer from '../components/DocumentViewer';
import axios from 'axios';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
  session_id?: string;
}

interface ChatHistory {
  question?: string;
  answer?: string;
  timestamp: string;
  sources?: any[];
}

export default function Home() {
  const { user, token, login, logout } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // États d'authentification
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  useEffect(() => {
    if (user && token) {
      fetchDocuments();
      fetchChatHistory();
    }
  }, [user, token]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/documents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des documents:', error);
    }
  };

  const fetchChatHistory = async () => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setChatHistory(response.data.history || []);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique:', error);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);
    try {
      await login(email, password);
    } catch (error) {
      console.error('Erreur de connexion:', error);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!currentQuestion.trim() || isLoading) return;

    const question = currentQuestion;
    setCurrentQuestion('');
    setIsLoading(true);

    // Ajouter la question à l'historique
    const newMessage: ChatHistory = {
      question,
      timestamp: new Date().toISOString()
    };
    setChatHistory(prev => [...prev, newMessage]);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/ask`,
        { question },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Ajouter la réponse à l'historique
      const answerMessage: ChatHistory = {
        answer: response.data.answer,
        timestamp: new Date().toISOString(),
        sources: response.data.sources
      };
      setChatHistory(prev => [...prev, answerMessage]);
    } catch (error) {
      console.error('Erreur lors de la question:', error);
      const errorMessage: ChatHistory = {
        answer: 'Désolé, une erreur est survenue lors du traitement de votre question.',
        timestamp: new Date().toISOString()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentSelect = (document: Document) => {
    setSelectedDocument(document);
  };

  const handleDocumentView = (document: Document) => {
    setSelectedDocument(document);
    setIsViewerOpen(true);
  };

  const handleDocumentDelete = async (document: Document) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) return;
    
    try {
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/documents/${document.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(prev => prev.filter(d => d.id !== document.id));
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center p-4">
        <Card variant="glass" className="w-full max-w-md">
          <CardContent className="p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-heading font-bold gradient-text mb-2">
                DocSearch AI
              </h1>
              <p className="text-text-muted">
                Connectez-vous pour accéder à votre assistant IA
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                placeholder="votre@email.com"
                required
                variant="glass"
              />
              
              <Input
                label="Mot de passe"
                type="password"
                value={password}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                variant="glass"
              />

              <Button
                type="submit"
                loading={isLoggingIn}
                className="w-full"
                size="lg"
              >
                Se connecter
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="glass border-b border-border-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-heading font-bold gradient-text">
                DocSearch AI
              </h1>
              <div className="flex items-center gap-2 text-sm text-text-muted">
                <span>Connecté en tant que</span>
                <span className="text-text-primary font-medium">{user.username}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => window.location.href = '/dashboard'}>
                📊 Tableau de bord
              </Button>
              <Button variant="ghost" onClick={logout}>
                🚪 Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Section Documents */}
          <div className="lg:col-span-1">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-heading font-semibold text-text-primary">
                📁 Documents
              </h2>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className={viewMode === 'grid' ? 'bg-bg-glass' : ''}
                >
                  ⊞
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className={viewMode === 'list' ? 'bg-bg-glass' : ''}
                >
                  ☰
                </Button>
              </div>
            </div>

            <div className={cn(
              'space-y-4',
              viewMode === 'grid' ? 'grid grid-cols-1 gap-4' : ''
            )}>
              {documents.map((doc) => (
                <DocumentCard
                  key={doc.id}
                  document={doc}
                  isSelected={selectedDocument?.id === doc.id}
                  onSelect={handleDocumentSelect}
                  onView={handleDocumentView}
                  onDelete={handleDocumentDelete}
                />
              ))}
              
              {documents.length === 0 && (
                <Card variant="glass" className="text-center py-12">
                  <div className="text-6xl mb-4">📄</div>
                  <p className="text-text-muted">
                    Aucun document disponible
                  </p>
                  <p className="text-sm text-text-muted mt-2">
                    Uploadez vos premiers documents pour commencer
                  </p>
                </Card>
              )}
            </div>
          </div>

          {/* Section Chat */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-heading font-semibold text-text-primary">
                💬 Assistant IA
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setChatHistory([])}
              >
                🗑️ Effacer
              </Button>
            </div>

            {/* Zone de chat */}
            <Card variant="glass" className="h-96 mb-4">
              <div className="h-full flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatHistory.map((message, index) => (
                    <ChatMessage
                      key={index}
                      message={message}
                      isUser={!!message.question}
                    />
                  ))}
                  
                  {isLoading && (
                    <ChatMessage
                      message={{ timestamp: new Date().toISOString() }}
                      isLoading={true}
                    />
                  )}
                </div>
              </div>
            </Card>

            {/* Input de question */}
            <div className="flex gap-4">
              <Input
                value={currentQuestion}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentQuestion(e.target.value)}
                placeholder="Posez votre question sur vos documents..."
                onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleAskQuestion()}
                variant="glass"
                className="flex-1"
              />
              <Button
                onClick={handleAskQuestion}
                disabled={!currentQuestion.trim() || isLoading}
                loading={isLoading}
                size="lg"
              >
                Envoyer
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Document Viewer Modal */}
      <DocumentViewer
        document={selectedDocument}
        isOpen={isViewerOpen}
        onClose={() => setIsViewerOpen(false)}
      />
    </div>
  );
}

function cn(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}
