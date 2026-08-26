import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors rounded-lg focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-sky-600 hover:bg-sky-700 text-white shadow-sm',
    secondary: 'bg-slate-800 hover:bg-slate-700 text-white',
    danger: 'bg-rose-600 hover:bg-rose-700 text-white shadow-sm',
    outline: 'border border-slate-300 text-slate-700 hover:bg-slate-50',
    ghost: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

interface CardProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ title, subtitle, action, children, className = '' }) => {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 shadow-sm p-6 ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && <h3 className="text-lg font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};

interface BadgeProps {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'neutral', children }) => {
  const badgeClasses = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-sky-50 text-sky-700 border-sky-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClasses[variant]}`}>
      {children}
    </span>
  );
};

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  icon?: React.ReactNode;
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, change, icon }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
        {change && <p className="text-xs font-medium text-emerald-600 mt-1">{change}</p>}
      </div>
      {icon && <div className="p-3 bg-sky-50 text-sky-600 rounded-lg">{icon}</div>}
    </div>
  );
};
