import React from 'react';
import Avatar from '../ui/Avatar';

interface ChatMessageProps {
  message: {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
    sources?: Array<{
      text: string;
      source: string;
      filename: string;
    }>;
  };
  index: number;
}

export default function ChatMessage({ message, index }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar 
          type="ai" 
          size="md" 
          className="flex-shrink-0 mt-2"
        />
      )}
      
      <div className={`flex flex-col max-w-3xl ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`p-4 rounded-lg border ${
            isUser 
              ? 'bg-blue-50 border-blue-200 text-gray-900' 
              : 'bg-gray-50 border-gray-200 text-gray-900'
          }`}
        >
          <div className="prose max-w-none">
            <p className="leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          </div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Sources :</h4>
              <div className="space-y-2">
                {message.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-white rounded border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <p className="text-xs text-gray-500 mb-1">{source.filename}</p>
                    <p className="text-sm text-gray-700 line-clamp-2">{source.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className="text-xs text-gray-500 mt-2 px-2">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
      
      {isUser && (
        <Avatar 
          type="user" 
          size="md" 
          className="flex-shrink-0 mt-2"
        />
      )}
    </div>
  );
} 