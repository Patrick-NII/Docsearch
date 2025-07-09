import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { getFileIcon } from '@/lib/utils';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
  content?: string;
  url?: string;
}

interface DocumentViewerProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document,
  isOpen,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'metadata'>('preview');

  if (!isOpen || !document) return null;

  const renderPreview = () => {
    const fileType = document.file_type.toLowerCase();
    
    if (fileType === 'pdf') {
      return (
        <div className="w-full h-96 bg-bg-secondary rounded-lg border border-border-light">
          <iframe
            src={document.url || `/api/documents/${document.id}/content`}
            className="w-full h-full rounded-lg"
            title={document.filename}
          />
        </div>
      );
    }
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileType)) {
      return (
        <div className="w-full max-h-96 overflow-hidden rounded-lg border border-border-light">
          <img
            src={document.url || `/api/documents/${document.id}/content`}
            alt={document.filename}
            className="w-full h-auto object-contain"
          />
        </div>
      );
    }
    
    if (['txt', 'md', 'json', 'xml', 'csv'].includes(fileType)) {
      return (
        <div className="w-full h-96 bg-bg-secondary rounded-lg border border-border-light p-4 overflow-auto">
          <pre className="text-sm text-text-primary font-mono whitespace-pre-wrap">
            {document.content || 'Contenu non disponible'}
          </pre>
        </div>
      );
    }
    
    return (
      <div className="w-full h-96 bg-bg-secondary rounded-lg border border-border-light flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">{getFileIcon(document.file_type)}</div>
          <p className="text-text-muted">
            Aperçu non disponible pour ce type de fichier
          </p>
          <Button
            variant="secondary"
            size="sm"
            className="mt-4"
            onClick={() => window.open(document.url || `/api/documents/${document.id}/content`, '_blank')}
          >
            Télécharger
          </Button>
        </div>
      </div>
    );
  };

  const renderMetadata = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-muted">Nom du fichier</label>
          <p className="text-text-primary">{document.filename}</p>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-muted">Type</label>
          <p className="text-text-primary">{document.file_type.toUpperCase()}</p>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-muted">Taille</label>
          <p className="text-text-primary">{document.file_size} bytes</p>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-muted">Date d'ajout</label>
          <p className="text-text-primary">{new Date(document.created_at).toLocaleDateString('fr-FR')}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card variant="glass" className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="flex items-center justify-between border-b border-border-light">
          <div className="flex items-center gap-3">
            <div className="text-2xl">{getFileIcon(document.file_type)}</div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">
                {document.filename}
              </h2>
              <p className="text-sm text-text-muted">
                Visualiseur de document
              </p>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="p-2"
          >
            ✕
          </Button>
        </CardHeader>
        
        <CardContent className="p-0">
          {/* Tabs */}
          <div className="flex border-b border-border-light">
            <button
              onClick={() => setActiveTab('preview')}
              className={`
                flex-1 px-4 py-3 text-sm font-medium transition-colors
                ${activeTab === 'preview' 
                  ? 'text-primary border-b-2 border-primary' 
                  : 'text-text-muted hover:text-text-primary'
                }
              `}
            >
              Aperçu
            </button>
            <button
              onClick={() => setActiveTab('metadata')}
              className={`
                flex-1 px-4 py-3 text-sm font-medium transition-colors
                ${activeTab === 'metadata' 
                  ? 'text-primary border-b-2 border-primary' 
                  : 'text-text-muted hover:text-text-primary'
                }
              `}
            >
              Métadonnées
            </button>
          </div>
          
          {/* Content */}
          <div className="p-6 max-h-96 overflow-auto">
            {activeTab === 'preview' ? renderPreview() : renderMetadata()}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentViewer; 