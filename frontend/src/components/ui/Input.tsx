import React from 'react';

interface InputProps {
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
  className?: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  error?: boolean;
}

export default function Input({ 
  value,
  onChange,
  placeholder,
  type = 'text',
  className = '',
  disabled = false,
  icon,
  error = false
}: InputProps) {
  const baseClasses = "w-full px-3 py-2 text-sm border rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500";
  
  const stateClasses = error 
    ? "border-red-300 bg-red-50 focus:border-red-500 focus:ring-red-500" 
    : "border-gray-300 bg-white focus:border-blue-500 focus:ring-blue-500";
  
  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed bg-gray-50" : "";

  return (
    <div className="relative">
      {icon && (
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
          {icon}
        </div>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`${baseClasses} ${stateClasses} ${disabledClasses} ${icon ? 'pl-10' : ''} ${className}`}
      />
    </div>
  );
} 