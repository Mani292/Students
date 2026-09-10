import React, { useState } from 'react';
import { Button } from '../components/UIComponents';
import { GraduationCap, ShieldCheck, UserCheck, Lock, ArrowLeft } from 'lucide-react';
import { login, registerStudent, type Session } from '../api';

interface AuthViewProps {
  onLogin: (session: Session) => void;
  onBack?: () => void;
}

export const AuthView: React.FC<AuthViewProps> = ({ onLogin, onBack }) => {
  const [email, setEmail] = useState('student@univ.edu');
  const [password, setPassword] = useState('password123');
  const [role, setRole] = useState<'STUDENT' | 'FACULTY' | 'ADMIN'>('STUDENT');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [fullName, setFullName] = useState('');
  const [rollNumber, setRollNumber] = useState('');
  const [departmentCode, setDepartmentCode] = useState('CSE');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const session = isRegistering
        ? await registerStudent(email, password, fullName, rollNumber, departmentCode)
        : await login(email, password);
      onLogin(session);
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : 'Unable to sign in');
    } finally {
      setIsSubmitting(false);
    }
  };

  const demoAccounts = [
    { role: 'STUDENT' as const, email: 'student@univ.edu', icon: <UserCheck className="h-5 w-5 mb-1" />, label: 'Student' },
    { role: 'FACULTY' as const, email: 'faculty@univ.edu', icon: <ShieldCheck className="h-5 w-5 mb-1" />, label: 'Faculty' },
    { role: 'ADMIN' as const,   email: 'admin@univ.edu',   icon: <Lock className="h-5 w-5 mb-1" />, label: 'Admin' },
  ];

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 px-4 relative overflow-hidden"
         style={{ background: 'hsl(var(--surface-1))' }}>

      {/* Background glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full opacity-10 blur-3xl pointer-events-none"
           style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.9), transparent)' }} />

      {/* Back button */}
      {onBack && (
        <button
          onClick={onBack}
          className="absolute top-6 left-6 flex items-center gap-2 text-sm text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text-primary))] transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </button>
      )}

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center relative z-10">
        <div className="inline-flex items-center justify-center p-3 rounded-2xl shadow-xl mb-4 animate-float"
             style={{ background: 'var(--gradient-primary)' }}>
          <GraduationCap className="h-9 w-9 text-white" />
        </div>
        <h2 className="text-3xl font-extrabold text-[hsl(var(--text-primary))] tracking-tight">SmartUniv Portal</h2>
        <p className="mt-2 text-sm text-[hsl(var(--text-secondary))]">AI-Powered University Digital Ecosystem</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="glass rounded-2xl p-8 shadow-2xl border-white/10 animate-fade-in-up">

          {/* Sign in / Register toggle */}
          <div className="flex gap-2 mb-6 p-1 rounded-xl"
               style={{ background: 'hsl(var(--surface-3))' }}>
            <button
              type="button"
              onClick={() => setIsRegistering(false)}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${!isRegistering ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-md' : 'text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text-primary))]'}`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => setIsRegistering(true)}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${isRegistering ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-md' : 'text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text-primary))]'}`}
            >
              Register
            </button>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>

            {/* Role selector (login only) */}
            {!isRegistering && (
              <div>
                <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] uppercase tracking-wide mb-2">Demo Account</label>
                <div className="grid grid-cols-3 gap-2">
                  {demoAccounts.map(d => (
                    <button
                      key={d.role}
                      type="button"
                      onClick={() => { setRole(d.role); setEmail(d.email); }}
                      className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all ${
                        role === d.role
                          ? 'bg-indigo-500/15 border-indigo-500/40 text-indigo-400'
                          : 'border-white/10 text-[hsl(var(--text-muted))] hover:bg-white/5 hover:text-[hsl(var(--text-primary))]'
                      }`}
                    >
                      {d.icon}
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Register extra fields */}
            {isRegistering && (
              <>
                <div>
                  <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Full Name</label>
                  <input required value={fullName} onChange={e => setFullName(e.target.value)} className="dark-input" placeholder="Raj Kumar" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Roll Number</label>
                  <input required value={rollNumber} onChange={e => setRollNumber(e.target.value)} className="dark-input" placeholder="2021CSE001" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Department Code</label>
                  <input required value={departmentCode} onChange={e => setDepartmentCode(e.target.value.toUpperCase())} className="dark-input" placeholder="CSE" />
                </div>
              </>
            )}

            <div>
              <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">University Email</label>
              <input type="email" required value={email} onChange={e => setEmail(e.target.value)} className="dark-input" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Password</label>
              <input type="password" required value={password} onChange={e => setPassword(e.target.value)} className="dark-input" />
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400 text-sm animate-fade-in">
                {error}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full glow-primary mt-2"
              loading={isSubmitting}
              disabled={isSubmitting}
            >
              {isRegistering ? 'Create Account' : 'Sign In to Ecosystem'}
            </Button>
          </form>

          {!isRegistering && (
            <p className="mt-4 text-center text-xs text-[hsl(var(--text-muted))]">
              Demo password: <span className="font-mono text-indigo-400">password123</span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
