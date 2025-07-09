import React, { useState } from 'react';
import { Card } from './ui/Card';
import { formatRelativeTime } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface Source {
  text: string;
  source: string;
  filename: string;
  file_type: string;
  page?: string;
}

interface ChatMessageProps {
  message: {
    question?: string;
    answer?: string;
    timestamp: string;
    sources?: Source[];
  };
  isUser?: boolean;
  isLoading?: boolean;
  className?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser = false,
  isLoading = false,
  className
}) => {
  const [showSources, setShowSources] = useState(false);

  const formatTimestamp = (timestamp: string) => {
    return formatRelativeTime(timestamp);
  };

  if (isUser && message.question) {
    return (
      <div className={cn('flex justify-end mb-4 animate-slide-in', className)}>
        <div className="max-w-[80%] lg:max-w-[70%]">
          <Card variant="glass" className="bg-primary/20 border-primary/30">
            <div className="p-4">
              <p className="text-text-primary whitespace-pre-wrap">
                {message.question}
              </p>
            </div>
          </Card>
          <div className="flex justify-end mt-2">
            <span className="text-xs text-text-muted">
              {formatTimestamp(message.timestamp)}
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (!isUser && message.answer) {
    return (
      <div className={cn('flex justify-start mb-4 animate-slide-in', className)}>
        <div className="max-w-[80%] lg:max-w-[70%]">
          {/* Avatar AI */}
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              AI
            </div>
            
            <div className="flex-1">
              <Card variant="glass" className="bg-bg-card/50">
                <div className="p-4">
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-pulse">🤔</div>
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="prose prose-invert max-w-none">
                        <p className="text-text-primary whitespace-pre-wrap leading-relaxed">
                          {message.answer}
                        </p>
                      </div>
                      
                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-border-light">
                          <button
                            onClick={() => setShowSources(!showSources)}
                            className="text-sm text-secondary hover:text-secondary/80 transition-colors flex items-center gap-2"
                          >
                            📚 {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                            <span className={cn(
                              'transition-transform duration-200',
                              showSources ? 'rotate-180' : ''
                            )}>
                              ▼
                            </span>
                          </button>
                          
                          {showSources && (
                            <div className="mt-3 space-y-2 animate-fade-in">
                              {message.sources.map((source, index) => (
                                <div
                                  key={index}
                                  className="p-3 bg-bg-glass rounded-lg border border-border-light"
                                >
                                  <div className="flex items-start justify-between mb-2">
                                    <span className="text-xs font-medium text-text-secondary">
                                      {source.filename}
                                    </span>
                                    <span className="text-xs text-text-muted">
                                      {source.file_type.toUpperCase()}
                                      {source.page && ` • Page ${source.page}`}
                                    </span>
                                  </div>
                                  <p className="text-sm text-text-muted leading-relaxed">
                                    "{source.text}"
                                  </p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </Card>
              
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs text-text-muted">
                  {formatTimestamp(message.timestamp)}
                </span>
                {!isLoading && (
                  <div className="flex items-center gap-1 text-xs text-text-muted">
                    <span>✓</span>
                    <span>Envoyé</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ChatMessage; 