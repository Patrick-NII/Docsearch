import React, { useState } from 'react';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { getFileIcon, formatFileSize, formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
  session_id?: string;
}

interface DocumentCardProps {
  document: Document;
  isSelected?: boolean;
  onSelect?: (document: Document) => void;
  onView?: (document: Document) => void;
  onDelete?: (document: Document) => void;
  className?: string;
}

const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  isSelected = false,
  onSelect,
  onView,
  onDelete,
  className
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    if (onSelect) {
      onSelect(document);
    }
  };

  const handleView = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onView) {
      onView(document);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(document);
    }
  };

  return (
    <Card
      variant="elevated"
      hover
      className={cn(
        'cursor-pointer transition-all duration-300',
        isSelected && 'ring-2 ring-primary ring-offset-2 ring-offset-bg-primary',
        className
      )}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardContent className="p-4">
        {/* Header avec icône et actions */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="text-2xl">{getFileIcon(document.file_type)}</div>
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-text-primary truncate">
                {document.filename}
              </h3>
              <p className="text-sm text-text-muted">
                {document.file_type.toUpperCase()} • {formatFileSize(document.file_size)}
              </p>
            </div>
          </div>
          
          {/* Actions au hover */}
          <div className={cn(
            'flex items-center gap-2 transition-all duration-300',
            isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-2'
          )}>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleView}
              className="p-1 h-8 w-8"
            >
              👁️
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleDelete}
              className="p-1 h-8 w-8 text-accent hover:text-red-400"
            >
              🗑️
            </Button>
          </div>
        </div>

        {/* Métadonnées */}
        <div className="flex items-center justify-between text-xs text-text-muted">
          <span>Ajouté {formatDate(document.created_at)}</span>
          {document.session_id && (
            <span className="px-2 py-1 bg-bg-glass rounded-full text-xs">
              Session active
            </span>
          )}
        </div>

        {/* Indicateur de sélection */}
        {isSelected && (
          <div className="absolute top-2 right-2 w-3 h-3 bg-primary rounded-full animate-pulse" />
        )}

        {/* Effet de sélection */}
        <div className={cn(
          'absolute inset-0 bg-primary opacity-0 transition-opacity duration-300 rounded-xl',
          isSelected && 'opacity-5'
        )} />
      </CardContent>
    </Card>
  );
};

export default DocumentCard; 