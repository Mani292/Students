import React, { useState, useEffect, useRef } from 'react';

// =================== BUTTON ===================
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost' | 'glass';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary', size = 'md', loading = false,
  className = '', children, disabled, ...props
}) => {
  const base = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-200 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed select-none';

  const variants = {
    primary:   'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg hover:from-blue-400 hover:to-indigo-500 hover:shadow-blue-500/30 hover:shadow-xl active:scale-[0.98]',
    secondary: 'bg-[hsl(var(--surface-3))] text-[hsl(var(--text-primary))] border border-[hsl(var(--surface-border))] hover:bg-[hsl(var(--surface-4))] active:scale-[0.98]',
    danger:    'bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-lg hover:from-red-500 hover:to-rose-500 hover:shadow-rose-500/30 hover:shadow-xl active:scale-[0.98]',
    outline:   'border border-indigo-500/40 text-indigo-400 hover:bg-indigo-500/10 hover:border-indigo-400 active:scale-[0.98]',
    ghost:     'text-[hsl(var(--text-secondary))] hover:bg-white/5 hover:text-[hsl(var(--text-primary))] active:scale-[0.98]',
    glass:     'bg-white/5 border border-white/10 text-[hsl(var(--text-primary))] backdrop-blur-sm hover:bg-white/10 hover:border-white/20 active:scale-[0.98]',
  };

  const sizes = {
    xs: 'px-2.5 py-1 text-[11px] gap-1',
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-6 py-3 text-base gap-2',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <LoadingSpinner size="sm" />}
      {children}
    </button>
  );
};

// =================== CARD ===================
interface CardProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  glass?: boolean;
  glow?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title, subtitle, action, children, className = '', glass = false, glow = false,
}) => {
  const base = glass
    ? 'glass rounded-xl p-6 shadow-md'
    : 'bg-[hsl(var(--surface-2))] border border-[hsl(var(--surface-border))] rounded-xl p-6 shadow-md';
  const glowClass = glow ? 'glow-card' : '';

  return (
    <div className={`${base} ${glowClass} ${className}`}>
      {(title || action) && (
        <div className="flex items-start justify-between mb-5">
          <div>
            {title && <h3 className="text-[15px] font-semibold text-[hsl(var(--text-primary))]">{title}</h3>}
            {subtitle && <p className="text-xs text-[hsl(var(--text-muted))] mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};

// =================== GLASS CARD ===================
export const GlassCard: React.FC<CardProps> = (props) => <Card {...props} glass />;

// =================== BADGE ===================
interface BadgeProps {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'purple';
  size?: 'sm' | 'md';
  children: React.ReactNode;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'neutral', size = 'sm', children, dot = false }) => {
  const variants = {
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
    danger:  'bg-red-500/15 text-red-400 border-red-500/25',
    info:    'bg-sky-500/15 text-sky-400 border-sky-500/25',
    neutral: 'bg-white/5 text-[hsl(var(--text-secondary))] border-white/10',
    purple:  'bg-indigo-500/15 text-indigo-400 border-indigo-500/25',
  };
  const dotColors = {
    success: 'bg-emerald-400', warning: 'bg-amber-400', danger: 'bg-red-400',
    info: 'bg-sky-400', neutral: 'bg-slate-400', purple: 'bg-indigo-400',
  };
  const sizes = { sm: 'px-2 py-0.5 text-[11px]', md: 'px-2.5 py-1 text-xs' };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium border ${variants[variant]} ${sizes[size]}`}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />}
      {children}
    </span>
  );
};

// =================== STAT CARD ===================
interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  iconColor?: string;
  animate?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  label, value, change, changeType = 'positive', icon, iconColor = 'from-blue-500 to-indigo-600', animate = true,
}) => {
  const changeColors = {
    positive: 'text-emerald-400',
    negative: 'text-red-400',
    neutral:  'text-[hsl(var(--text-muted))]',
  };

  return (
    <div className={`bg-[hsl(var(--surface-2))] border border-[hsl(var(--surface-border))] rounded-xl p-5 flex items-start justify-between hover:border-indigo-500/30 transition-all duration-200 ${animate ? 'animate-count' : ''}`}>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-[hsl(var(--text-muted))] uppercase tracking-wide truncate">{label}</p>
        <p className="text-2xl font-bold text-[hsl(var(--text-primary))] mt-1.5 leading-none">{value}</p>
        {change && <p className={`text-xs font-medium mt-1.5 ${changeColors[changeType]}`}>{change}</p>}
      </div>
      {icon && (
        <div className={`p-2.5 rounded-xl bg-gradient-to-br ${iconColor} text-white shadow-lg flex-shrink-0`}>
          {icon}
        </div>
      )}
    </div>
  );
};

// =================== PROGRESS BAR ===================
interface ProgressBarProps {
  value: number;        // 0–100
  label?: string;
  showValue?: boolean;
  height?: number;
  color?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value, label, showValue = true, height = 8, color = 'var(--gradient-primary)',
}) => {
  const [displayed, setDisplayed] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setDisplayed(Math.min(100, Math.max(0, value))), 100);
    return () => clearTimeout(t);
  }, [value]);

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-1.5">
          {label && <span className="text-xs text-[hsl(var(--text-secondary))]">{label}</span>}
          {showValue && <span className="text-xs font-semibold text-[hsl(var(--text-primary))]">{value}%</span>}
        </div>
      )}
      <div className="progress-track w-full" style={{ height }}>
        <div className="progress-fill" style={{ width: `${displayed}%`, background: color }} />
      </div>
    </div>
  );
};

// =================== AVATAR ===================
interface AvatarProps {
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  src?: string;
}

export const Avatar: React.FC<AvatarProps> = ({ name = '?', size = 'md', src }) => {
  const sizes = { sm: 'w-7 h-7 text-xs', md: 'w-9 h-9 text-sm', lg: 'w-12 h-12 text-base', xl: 'w-16 h-16 text-xl' };
  const initials = name.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase();

  if (src) return <img src={src} className={`${sizes[size]} rounded-full object-cover ring-2 ring-white/10`} alt={name} />;
  return (
    <div className={`${sizes[size]} rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white font-bold flex items-center justify-center ring-2 ring-white/10 flex-shrink-0`}>
      {initials}
    </div>
  );
};

// =================== LOADING SPINNER ===================
interface SpinnerProps { size?: 'sm' | 'md' | 'lg'; }

export const LoadingSpinner: React.FC<SpinnerProps> = ({ size = 'md' }) => {
  const sizes = { sm: 'w-3.5 h-3.5 border-2', md: 'w-5 h-5 border-2', lg: 'w-8 h-8 border-3' };
  return (
    <div
      className={`${sizes[size]} rounded-full border-current border-t-transparent opacity-70 animate-spin`}
      style={{ animation: 'spin-slow 0.8s linear infinite' }}
    />
  );
};

// =================== MODAL ===================
interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Modal: React.FC<ModalProps> = ({ open, onClose, title, children, size = 'md' }) => {
  const sizeClass = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' };
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (open) window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div className={`w-full ${sizeClass[size]} glass rounded-2xl shadow-2xl animate-fade-in-up`}
           style={{ border: '1px solid rgba(255,255,255,0.1)' }}>
        {title && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
            <h3 className="font-semibold text-[hsl(var(--text-primary))]">{title}</h3>
            <button onClick={onClose} className="text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text-primary))] transition-colors p-1 rounded-lg hover:bg-white/5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        )}
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

// =================== TOOLTIP ===================
interface TooltipProps {
  content: string;
  children: React.ReactNode;
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-flex" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 text-xs rounded-lg bg-[hsl(var(--surface-4))] text-[hsl(var(--text-primary))] border border-white/10 whitespace-nowrap shadow-lg z-50 pointer-events-none animate-fade-in">
          {content}
        </div>
      )}
    </div>
  );
};

// =================== TYPING INDICATOR ===================
export const TypingIndicator: React.FC = () => (
  <div className="flex items-center gap-1 px-3 py-2 bg-[hsl(var(--surface-3))] rounded-2xl w-fit">
    <span className="typing-dot" />
    <span className="typing-dot" />
    <span className="typing-dot" />
  </div>
);

// =================== EMPTY STATE ===================
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    {icon && <div className="mb-4 text-[hsl(var(--text-muted))] opacity-40">{icon}</div>}
    <p className="text-sm font-semibold text-[hsl(var(--text-secondary))]">{title}</p>
    {description && <p className="text-xs text-[hsl(var(--text-muted))] mt-1 max-w-xs">{description}</p>}
    {action && <div className="mt-4">{action}</div>}
  </div>
);

// =================== DIVIDER ===================
export const Divider: React.FC<{ label?: string }> = ({ label }) => (
  <div className="relative flex items-center my-4">
    <div className="flex-1 border-t border-white/10" />
    {label && <span className="mx-3 text-xs text-[hsl(var(--text-muted))]">{label}</span>}
    {label && <div className="flex-1 border-t border-white/10" />}
  </div>
);

// =================== ALERT ===================
interface AlertProps {
  type?: 'success' | 'warning' | 'danger' | 'info';
  children: React.ReactNode;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type = 'info', children, onClose }) => {
  const styles = {
    success: 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400',
    warning: 'bg-amber-500/10 border-amber-500/25 text-amber-400',
    danger:  'bg-red-500/10 border-red-500/25 text-red-400',
    info:    'bg-sky-500/10 border-sky-500/25 text-sky-400',
  };
  return (
    <div className={`flex items-start gap-3 p-3.5 rounded-xl border text-sm animate-fade-in ${styles[type]}`}>
      <span className="flex-1">{children}</span>
      {onClose && (
        <button onClick={onClose} className="opacity-60 hover:opacity-100 transition-opacity mt-0.5">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      )}
    </div>
  );
};
