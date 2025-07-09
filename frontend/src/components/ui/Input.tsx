import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'glass' | 'outline';
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, variant = 'default', className, ...props }, ref) => {
    const baseClasses = `
      w-full px-4 py-3 text-base
      bg-transparent border rounded-lg
      transition-all duration-300
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent
      placeholder:text-text-muted
      disabled:opacity-50 disabled:cursor-not-allowed
      relative
    `;

    const variantClasses = {
      default: `
        bg-bg-card border-border-light
        hover:border-border-medium focus:border-primary
        focus:ring-primary
        shadow-sm hover:shadow-md
      `,
      glass: `
        bg-bg-glass border-border-light backdrop-blur-sm
        hover:border-border-medium focus:border-secondary
        focus:ring-secondary
        shadow-lg hover:shadow-xl
      `,
      outline: `
        bg-transparent border-2 border-border-light
        hover:border-border-medium focus:border-primary
        focus:ring-primary
      `
    };

    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-text-primary">
            {label}
          </label>
        )}
        
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-muted">
              {icon}
            </div>
          )}
          
          <input
            ref={ref}
            className={cn(
              baseClasses,
              variantClasses[variant],
              icon && 'pl-10',
              error && 'border-accent focus:border-accent focus:ring-accent',
              className
            )}
            {...props}
          />
          
          {/* Effet de brillance au focus */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 focus-within:opacity-5 transition-opacity duration-300 pointer-events-none rounded-lg" />
        </div>
        
        {error && (
          <p className="text-sm text-accent animate-slide-in">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input; 