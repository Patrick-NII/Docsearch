import React from 'react';

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'subtle';
}

export default function GlassPanel({ 
  children, 
  className = '', 
  variant = 'default'
}: GlassPanelProps) {
  const baseClasses = "border border-gray-200 rounded-lg shadow-sm";
  
  const variantClasses = {
    default: "bg-white",
    elevated: "bg-white shadow-md",
    subtle: "bg-gray-50"
  };

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    >
      {children}
    </div>
  );
} 