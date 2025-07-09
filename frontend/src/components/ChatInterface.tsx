'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './AuthContext';
import axios from 'axios';

interface Message {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
  sources?: Array<{
    text: string;
    source: string;
    filename: string;
    file_type: string;
    page: string;
    session_id: string;
  }>;
}

interface ChatInterfaceProps {
  selectedDocument?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ selectedDocument }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        const history = response.data.history.map((msg: any, index: number) => ({
          id: `history-${index}`,
          question: msg.question,
          answer: msg.answer,
          timestamp: msg.timestamp,
          sources: msg.sources || []
        }));
        setMessages(history);
      }
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique:', error);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else {
      return date.toLocaleDateString('fr-FR', { 
        day: '2-digit', 
        month: '2-digit',
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const question = inputValue.trim();
    setInputValue('');
    setIsLoading(true);
    setIsTyping(true);

    // Ajouter le message utilisateur immédiatement
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      question,
      answer: '',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/ask`, {
        question,
        session_id: selectedDocument
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        const aiMessage: Message = {
          id: `ai-${Date.now()}`,
          question: '',
          answer: response.data.answer,
          timestamp: new Date().toISOString(),
          sources: response.data.sources || []
        };

        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Erreur lors de l\'envoi de la question:', error);
      
      // Message d'erreur
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        question: '',
        answer: 'Désolé, une erreur s\'est produite. Veuillez réessayer.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages([]);
    } catch (error) {
      console.error('Erreur lors de l\'effacement de l\'historique:', error);
    }
  };

  return (
    <div className="flex flex-col h-full max-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between p-6 glass border-b border-border-light">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary">Chat IA</h1>
            <p className="text-sm text-text-secondary">
              {selectedDocument ? `Document sélectionné: ${selectedDocument}` : 'Posez vos questions'}
            </p>
          </div>
        </div>
        
        <button
          onClick={clearHistory}
          className="btn-secondary text-sm"
          title="Effacer l'historique"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Effacer
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Bienvenue sur DocSearch AI
            </h3>
            <p className="text-text-secondary max-w-md">
              Posez vos questions sur vos documents. Je peux vous aider à analyser, résumer et extraire des informations.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={message.id} className={`animate-fade-in ${index === messages.length - 1 ? 'animate-slide-in' : ''}`}>
              {/* Message utilisateur */}
              {message.question && (
                <div className="flex justify-end mb-4">
                  <div className="max-w-3xl">
                    <div className="bg-gradient-primary rounded-2xl rounded-br-md px-6 py-4 shadow-lg">
                      <p className="text-white font-medium">{message.question}</p>
                    </div>
                    <div className="flex justify-end mt-2">
                      <span className="text-xs text-text-muted">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Message IA */}
              {message.answer && (
                <div className="flex justify-start mb-4">
                  <div className="max-w-3xl">
                    <div className="card-glass rounded-2xl rounded-bl-md px-6 py-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-gradient-secondary rounded-full flex items-center justify-center flex-shrink-0">
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <div className="prose prose-invert max-w-none">
                            <p className="text-text-primary whitespace-pre-wrap">{message.answer}</p>
                          </div>
                          
                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-border-light">
                              <h4 className="text-sm font-semibold text-text-accent mb-2">Sources :</h4>
                              <div className="space-y-2">
                                {message.sources.map((source, idx) => (
                                  <div key={idx} className="p-3 rounded-lg bg-bg-glass border border-border-light">
                                    <div className="flex items-center justify-between mb-1">
                                      <span className="text-xs font-medium text-text-secondary">
                                        {source.filename} ({source.file_type})
                                      </span>
                                      <span className="text-xs text-text-muted">
                                        Page {source.page}
                                      </span>
                                    </div>
                                    <p className="text-xs text-text-secondary line-clamp-2">
                                      {source.text}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-start mt-2">
                      <span className="text-xs text-text-muted">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start mb-4 animate-fade-in">
            <div className="max-w-3xl">
              <div className="card-glass rounded-2xl rounded-bl-md px-6 py-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-secondary rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-text-accent rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-text-accent rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-text-accent rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 glass border-t border-border-light">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Posez votre question..."
              className="input-modern w-full resize-none pr-12"
              rows={1}
              disabled={isLoading}
              style={{
                minHeight: '48px',
                maxHeight: '120px'
              }}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-lg bg-gradient-primary disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow transition-all"
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
        
        <div className="flex items-center justify-between mt-3 text-xs text-text-muted">
          <span>Appuyez sur Entrée pour envoyer, Shift+Entrée pour une nouvelle ligne</span>
          <span>{inputValue.length} caractères</span>
        </div>
      </div>
    </div>
  );
}; 