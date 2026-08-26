import React, { useEffect, useState } from 'react';
import { AuthView } from './views/AuthView';
import { StudentPortal } from './views/StudentPortal';
import { FacultyDashboard } from './views/FacultyDashboard';
import { AdminDashboard } from './views/AdminDashboard';
import { refreshSession, type Session } from './api';

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

  const handleLogin = (nextSession: Session) => {
    setSession(nextSession);
    localStorage.setItem('smart-university-session', JSON.stringify(nextSession));
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
  };

  if (!session) {
    return <AuthView onLogin={handleLogin} />;
  }

  if (session.user.role === 'STUDENT') {
    return <StudentPortal userEmail={session.user.email} token={session.token} onLogout={handleLogout} />;
  }

  if (session.user.role === 'FACULTY') {
    return <FacultyDashboard userEmail={session.user.email} token={session.token} onLogout={handleLogout} />;
  }

  if (session.user.role === 'ADMIN' || session.user.role === 'SUPER_ADMIN' || session.user.role === 'HOD') {
    return <AdminDashboard userEmail={session.user.email} token={session.token} onLogout={handleLogout} />;
  }

  return <AuthView onLogin={handleLogin} />;
};

export default App;
