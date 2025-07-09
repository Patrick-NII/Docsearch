import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
}

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '',
  onClick,
  disabled = false,
  loading = false,
  icon
}: ButtonProps) {
  const baseClasses = "relative font-medium transition-all duration-150 rounded-md border";
  
  const variantClasses = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white border-blue-600 shadow-sm",
    secondary: "bg-gray-100 hover:bg-gray-200 text-gray-900 border-gray-200",
    ghost: "bg-transparent hover:bg-gray-50 text-gray-700 border-transparent",
    danger: "bg-red-600 hover:bg-red-700 text-white border-red-600 shadow-sm"
  };

  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  };

  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:transform hover:-translate-y-0.5";

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses} ${className}`}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
        </div>
      )}
      
      <div className={`flex items-center justify-center gap-2 ${loading ? 'opacity-0' : ''}`}>
        {icon && <span className="text-base">{icon}</span>}
        {children}
      </div>
    </button>
  );
} 