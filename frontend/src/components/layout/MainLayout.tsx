import React from 'react';
import Sidebar from '../sidebar/Sidebar';
import ChatContainer from '../chat/ChatContainer';

interface MainLayoutProps {
  children?: React.ReactNode;
  documents?: any[];
  messages?: any[];
  onSendMessage?: (message: string) => void;
  onDocumentSelect?: (docId: string) => void;
  onUploadDocument?: () => void;
  onDeleteDocument?: (docId: string) => void;
  selectedDocumentId?: string;
  user?: any;
  loading?: boolean;
}

export default function MainLayout({
  children,
  documents = [],
  messages = [],
  onSendMessage,
  onDocumentSelect,
  onUploadDocument,
  onDeleteDocument,
  selectedDocumentId,
  user,
  loading = false
}: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-white">
      {/* Main Content */}
      <div className="flex h-screen max-w-7xl mx-auto">
        {/* Sidebar */}
        <div className="flex-shrink-0 w-full max-w-xs">
          <Sidebar
            documents={documents}
            onDocumentSelect={onDocumentSelect}
            onUploadDocument={onUploadDocument}
            onDeleteDocument={onDeleteDocument}
            selectedDocumentId={selectedDocumentId}
            user={user}
          />
        </div>

        {/* Main Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {children || (
            <ChatContainer
              messages={messages}
              onSendMessage={onSendMessage}
              loading={loading}
            />
          )}
        </div>
      </div>
    </div>
  );
} 