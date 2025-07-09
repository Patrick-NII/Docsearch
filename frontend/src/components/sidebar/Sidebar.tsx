import React, { useState } from 'react';
import { 
  DocumentTextIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon,
  UserIcon,
  Cog6ToothIcon,
  PlusIcon,
  FolderIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import GlassPanel from '../ui/GlassPanel';
import Button from '../ui/Button';
import Avatar from '../ui/Avatar';

interface Document {
  id: string;
  name: string;
  type: string;
  size: string;
  uploaded_at: string;
}

interface SidebarProps {
  documents: Document[];
  onDocumentSelect: (docId: string) => void;
  onUploadDocument: () => void;
  onDeleteDocument: (docId: string) => void;
  selectedDocumentId?: string;
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
}

export default function Sidebar({
  documents,
  onDocumentSelect,
  onUploadDocument,
  onDeleteDocument,
  selectedDocumentId,
  user
}: SidebarProps) {
  const [activeTab, setActiveTab] = useState<'documents' | 'chat' | 'analytics' | 'profile'>('documents');
  const [hoveredDoc, setHoveredDoc] = useState<string | null>(null);

  const tabs = [
    { id: 'documents', label: 'Documents', icon: DocumentTextIcon },
    { id: 'chat', label: 'Chat', icon: ChatBubbleLeftRightIcon },
    { id: 'analytics', label: 'Analytics', icon: ChartBarIcon },
    { id: 'profile', label: 'Profile', icon: UserIcon },
  ];

  return (
    <div className="w-full max-w-xs h-full flex flex-col bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <DocumentTextIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-gray-900">DocSearch</h2>
            <p className="text-xs text-gray-500">AI Assistant</p>
          </div>
        </div>

        {/* Upload Button */}
        <Button
          onClick={onUploadDocument}
          icon={<PlusIcon className="w-4 h-4" />}
          className="w-full"
          size="sm"
        >
          Ajouter un doc
        </Button>
      </div>

      {/* Navigation Tabs */}
      <div className="p-2">
        <div className="flex flex-col space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors duration-150 text-sm ${
                activeTab === tab.id
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-2">
        {activeTab === 'documents' && (
          <div className="h-full flex flex-col">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Documents</h3>
            
            <div className="flex-1 overflow-y-auto space-y-1">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  onMouseEnter={() => setHoveredDoc(doc.id)}
                  onMouseLeave={() => setHoveredDoc(null)}
                  className={`relative p-2 rounded-md border transition-colors duration-150 cursor-pointer ${
                    selectedDocumentId === doc.id
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                  }`}
                  onClick={() => onDocumentSelect(doc.id)}
                >
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center">
                      <FolderIcon className="w-3.5 h-3.5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-gray-900 font-medium truncate text-sm">{doc.name}</p>
                      <p className="text-xs text-gray-500">{doc.type} • {doc.size}</p>
                    </div>
                  </div>

                  {hoveredDoc === doc.id && (
                    <div className="absolute right-1 top-1/2 -translate-y-1/2 flex gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // View document
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                      >
                        <EyeIcon className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteDocument(doc.id);
                        }}
                        className="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                      >
                        <TrashIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="h-full">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Profile</h3>
            
            {user && (
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <div className="flex items-center gap-3 mb-3">
                  <Avatar
                    src={user.avatar}
                    alt={user.name}
                    size="md"
                    type="user"
                  />
                  <div>
                    <p className="text-gray-900 font-semibold text-sm">{user.name}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>
                </div>
                
                <Button
                  variant="secondary"
                  icon={<Cog6ToothIcon className="w-4 h-4" />}
                  className="w-full"
                  size="sm"
                >
                  Paramètres
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 