import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'elevated' | 'bordered';
  hover?: boolean;
  children: React.ReactNode;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  hover = false,
  children,
  className,
  ...props
}) => {
  const baseClasses = `
    rounded-xl transition-all duration-300
    relative overflow-hidden
  `;

  const variantClasses = {
    default: `
      bg-bg-card border border-border-light
      shadow-soft
    `,
    glass: `
      bg-bg-glass border border-border-light
      backdrop-blur-xl shadow-strong
    `,
    elevated: `
      bg-bg-card border border-border-light
      shadow-strong hover:shadow-glow
      transform hover:-translate-y-1
    `,
    bordered: `
      bg-transparent border-2 border-border-light
      hover:border-border-medium
    `
  };

  const hoverClasses = hover ? 'hover:scale-[1.02] hover:shadow-xl' : '';

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        hoverClasses,
        className
      )}
      {...props}
    >
      {/* Effet de brillance au hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 hover:opacity-5 transition-opacity duration-300 pointer-events-none" />
      
      {/* Contenu */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardHeader: React.FC<CardHeaderProps> = ({ children, className, ...props }) => (
  <div className={cn('p-6 pb-0', className)} {...props}>
    {children}
  </div>
);

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardContent: React.FC<CardContentProps> = ({ children, className, ...props }) => (
  <div className={cn('p-6', className)} {...props}>
    {children}
  </div>
);

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardFooter: React.FC<CardFooterProps> = ({ children, className, ...props }) => (
  <div className={cn('p-6 pt-0', className)} {...props}>
    {children}
  </div>
);

export { Card, CardHeader, CardContent, CardFooter }; 