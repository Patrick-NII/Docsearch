'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import MainLayout from '../components/layout/MainLayout';
import Hero from '../components/landing/Hero';

export default function HomePage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [messages, setMessages] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    if (isAuthenticated) {
      // Simulate loading documents
      setDocuments([
        { id: '1', name: 'Contrat.pdf', type: 'PDF', size: '1.2MB', uploaded_at: '2024-07-09' },
        { id: '2', name: 'Rapport.docx', type: 'DOCX', size: '800KB', uploaded_at: '2024-07-08' },
      ]);
      setMessages([
        { id: '1', content: 'Bonjour, que puis-je faire pour vous ?', role: 'assistant', timestamp: '09:00' },
      ]);
    }
  }, [isAuthenticated]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-gray-900 text-lg">Chargement...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Landing page
    return <Hero />;
  }

  // Main app
  return (
    <MainLayout
      documents={documents}
      messages={messages}
      onSendMessage={(msg) => {
        setLoading(true);
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { id: String(prev.length + 1), content: msg, role: 'user', timestamp: '09:01' },
            { id: String(prev.length + 2), content: 'Réponse IA simulée.', role: 'assistant', timestamp: '09:01' },
          ]);
          setLoading(false);
        }, 800);
      }}
      onDocumentSelect={setSelectedDocumentId}
      onUploadDocument={() => {
        console.log('Upload document');
      }}
      onDeleteDocument={(docId) => {
        setDocuments(prev => prev.filter(doc => doc.id !== docId));
      }}
      selectedDocumentId={selectedDocumentId}
      user={user}
      loading={loading}
    />
  );
}
