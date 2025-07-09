import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  children,
  className,
  disabled,
  ...props
}) => {
  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-medium transition-all duration-300
    border border-transparent rounded-lg
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent
    disabled:opacity-50 disabled:cursor-not-allowed
    relative overflow-hidden group
  `;

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const variantClasses = {
    primary: `
      bg-gradient-to-r from-primary to-primary-dark
      hover:from-primary-dark hover:to-primary
      text-white shadow-lg hover:shadow-xl
      focus:ring-primary
      before:absolute before:inset-0 before:bg-white before:opacity-0 before:transition-opacity
      hover:before:opacity-10
    `,
    secondary: `
      bg-gradient-to-r from-secondary to-blue-500
      hover:from-blue-500 hover:to-secondary
      text-white shadow-lg hover:shadow-xl
      focus:ring-secondary
      before:absolute before:inset-0 before:bg-white before:opacity-0 before:transition-opacity
      hover:before:opacity-10
    `,
    ghost: `
      bg-transparent border-border-light
      hover:bg-bg-glass hover:border-border-medium
      text-text-primary hover:text-white
      focus:ring-border-medium
    `,
    danger: `
      bg-gradient-to-r from-accent to-red-500
      hover:from-red-500 hover:to-accent
      text-white shadow-lg hover:shadow-xl
      focus:ring-accent
      before:absolute before:inset-0 before:bg-white before:opacity-0 before:transition-opacity
      hover:before:opacity-10
    `,
    success: `
      bg-gradient-to-r from-green-500 to-emerald-500
      hover:from-emerald-500 hover:to-green-500
      text-white shadow-lg hover:shadow-xl
      focus:ring-green-500
      before:absolute before:inset-0 before:bg-white before:opacity-0 before:transition-opacity
      hover:before:opacity-10
    `
  };

  return (
    <button
      className={cn(
        baseClasses,
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
      )}
      {!loading && icon && <span className="flex-shrink-0">{icon}</span>}
      <span className="relative z-10">{children}</span>
      
      {/* Effet de brillance au hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 group-hover:animate-pulse transition-opacity duration-300" />
    </button>
  );
};

export default Button; 