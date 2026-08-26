import React, { useState } from 'react';
import { Button, Card } from '../components/UIComponents';
import { GraduationCap, ShieldCheck, UserCheck, Lock } from 'lucide-react';
import { login, type SessionUser } from '../api';

interface AuthViewProps {
  onLogin: (session: { token: string; user: SessionUser }) => void;
}

export const AuthView: React.FC<AuthViewProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('student@univ.edu');
  const [password, setPassword] = useState('password123');
  const [role, setRole] = useState<'STUDENT' | 'FACULTY' | 'ADMIN'>('STUDENT');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const session = await login(email, password);
      onLogin(session);
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : 'Unable to sign in');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center p-3 bg-sky-600 text-white rounded-2xl shadow-xl mb-4">
          <GraduationCap className="h-10 w-10" />
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Smart University Portal</h2>
        <p className="mt-2 text-sm text-slate-400">AI-Powered Centralized Digital Ecosystem</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="bg-white border-none shadow-2xl p-8 rounded-2xl">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Select Account Role</label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => { setRole('STUDENT'); setEmail('student@univ.edu'); }}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all ${
                    role === 'STUDENT' ? 'border-sky-600 bg-sky-50 text-sky-700 ring-2 ring-sky-600/20' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <UserCheck className="h-5 w-5 mb-1" />
                  Student
                </button>
                <button
                  type="button"
                  onClick={() => { setRole('FACULTY'); setEmail('faculty@univ.edu'); }}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all ${
                    role === 'FACULTY' ? 'border-sky-600 bg-sky-50 text-sky-700 ring-2 ring-sky-600/20' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <ShieldCheck className="h-5 w-5 mb-1" />
                  Faculty
                </button>
                <button
                  type="button"
                  onClick={() => { setRole('ADMIN'); setEmail('admin@univ.edu'); }}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all ${
                    role === 'ADMIN' ? 'border-sky-600 bg-sky-50 text-sky-700 ring-2 ring-sky-600/20' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <Lock className="h-5 w-5 mb-1" />
                  Admin
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">University Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 text-sm"
              />
            </div>

            {error && <p role="alert" className="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-3">{error}</p>}

            <Button type="submit" variant="primary" size="lg" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign In to Ecosystem'}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
};
