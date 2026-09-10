import React, { useEffect, useState } from 'react';
import { LandingPage } from './views/LandingPage';
import { AuthView } from './views/AuthView';
import { StudentPortal } from './views/StudentPortal';
import { FacultyDashboard } from './views/FacultyDashboard';
import { AdminDashboard } from './views/AdminDashboard';
import { refreshSession, type Session } from './api';

type AppScreen = 'landing' | 'auth' | 'dashboard';

export const App: React.FC = () => {
  const [session, setSession] = useState<Session | null>(() => {
    const stored = localStorage.getItem('smart-university-session');
    if (!stored) return null;
    try {
      return JSON.parse(stored) as Session;
    } catch {
      localStorage.removeItem('smart-university-session');
      return null;
    }
  });

  // When there's no session, start on landing. When logged out, go back to landing.
  const [screen, setScreen] = useState<AppScreen>(() => (session ? 'dashboard' : 'landing'));

  const handleLogin = (nextSession: Session) => {
    setSession(nextSession);
    localStorage.setItem('smart-university-session', JSON.stringify(nextSession));
    setScreen('dashboard');
  };

  useEffect(() => {
    if (!session?.refreshToken) return;
    refreshSession(session.refreshToken)
      .then(handleLogin)
      .catch(handleLogout);
  }, []);

  const handleLogout = () => {
    setSession(null);
    localStorage.removeItem('smart-university-session');
    setScreen('landing');
  };

  // ── Landing ──
  if (screen === 'landing') {
    return <LandingPage onGetStarted={() => setScreen('auth')} />;
  }

  // ── Auth ──
  if (screen === 'auth' || !session) {
    return <AuthView onLogin={handleLogin} onBack={() => setScreen('landing')} />;
  }

  // ── Dashboard ──
  const { email, role } = session.user;
  const token = session.token;

  if (role === 'STUDENT') {
    return <StudentPortal userEmail={email} token={token} onLogout={handleLogout} />;
  }
  if (role === 'FACULTY') {
    return <FacultyDashboard userEmail={email} token={token} onLogout={handleLogout} />;
  }
  if (['ADMIN', 'SUPER_ADMIN', 'HOD'].includes(role)) {
    return <AdminDashboard userEmail={email} token={token} onLogout={handleLogout} />;
  }

  return <AuthView onLogin={handleLogin} onBack={() => setScreen('landing')} />;
};

export default App;
