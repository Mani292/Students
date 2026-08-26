import React, { useState } from 'react';
import { AuthView } from './views/AuthView';
import { StudentPortal } from './views/StudentPortal';
import { FacultyDashboard } from './views/FacultyDashboard';
import { AdminDashboard } from './views/AdminDashboard';
import type { SessionUser } from './api';

export const App: React.FC = () => {
  const [session, setSession] = useState<{ token: string; user: SessionUser } | null>(null);

  const handleLogin = (nextSession: { token: string; user: SessionUser }) => {
    setSession(nextSession);
  };

  const handleLogout = () => {
    setSession(null);
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
    return <AdminDashboard userEmail={session.user.email} onLogout={handleLogout} />;
  }

  return <AuthView onLogin={handleLogin} />;
};

export default App;
