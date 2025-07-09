'use client';

import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { ChatInterface } from '../components/ChatInterface';
import { DocumentManager } from '../components/DocumentManager';

export default function HomePage() {
  const [selectedDocument, setSelectedDocument] = useState<string>('');
  const [showDocuments, setShowDocuments] = useState(false);

  return (
    <Layout>
      <div className="flex h-screen">
        {/* Document Manager Sidebar */}
        <div className={`w-80 border-r border-border-light transition-all duration-300 ${
          showDocuments ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:inset-0`}>
          <div className="h-full overflow-y-auto">
            <DocumentManager
              onDocumentSelect={setSelectedDocument}
              selectedDocument={selectedDocument}
            />
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 flex flex-col">
          <ChatInterface selectedDocument={selectedDocument} />
        </div>

        {/* Mobile Toggle */}
        <button
          onClick={() => setShowDocuments(!showDocuments)}
          className="lg:hidden fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-primary rounded-full flex items-center justify-center shadow-lg hover:shadow-glow transition-all"
        >
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </button>
      </div>
    </Layout>
  );
}
