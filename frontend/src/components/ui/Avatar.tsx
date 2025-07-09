import React from 'react';

interface AvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  type?: 'user' | 'ai' | 'default';
  className?: string;
}

export default function Avatar({ 
  src, 
  alt = 'Avatar', 
  size = 'md', 
  type = 'default',
  className = ''
}: AvatarProps) {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg'
  };

  const typeStyles = {
    user: {
      bg: 'bg-blue-600',
      icon: '👤'
    },
    ai: {
      bg: 'bg-green-600',
      icon: '🤖'
    },
    default: {
      bg: 'bg-gray-600',
      icon: '👤'
    }
  };

  const style = typeStyles[type];

  if (src) {
    return (
      <div
        className={`${sizeClasses[size]} rounded-full overflow-hidden shadow-sm border border-gray-200 ${className}`}
      >
        <img 
          src={src} 
          alt={alt} 
          className="w-full h-full object-cover"
        />
      </div>
    );
  }

  return (
    <div
      className={`${sizeClasses[size]} ${style.bg} rounded-full flex items-center justify-center text-white font-medium shadow-sm ${className}`}
    >
      <span className="text-lg">{style.icon}</span>
    </div>
  );
} 