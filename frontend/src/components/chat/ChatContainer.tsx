import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  sources?: Array<{
    text: string;
    source: string;
    filename: string;
  }>;
}

interface ChatContainerProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  loading?: boolean;
  disabled?: boolean;
}

export default function ChatContainer({ 
  messages, 
  onSendMessage, 
  loading = false,
  disabled = false 
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 max-w-3xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 bg-green-500 rounded-full" />
          <h1 className="text-lg font-semibold text-gray-900">DocSearch AI</h1>
          <span className="text-xs text-gray-500">Assistant IA</span>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-4 max-w-3xl mx-auto w-full space-y-4" style={{minHeight:'0'}}>
        {messages.map((message, index) => (
          <ChatMessage
            key={message.id}
            message={message}
            index={index}
          />
        ))}
        
        {loading && (
          <div className="flex gap-4 mb-6">
            <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-medium">
              🤖
            </div>
            <div className="flex flex-col max-w-2xl">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" />
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="max-w-3xl mx-auto w-full p-4">
        <ChatInput
          onSend={onSendMessage}
          disabled={disabled}
          loading={loading}
        />
      </div>
    </div>
  );
} 