import React, { useState } from 'react';
import { AuthView } from './views/AuthView';
import { StudentPortal } from './views/StudentPortal';
import { FacultyDashboard } from './views/FacultyDashboard';
import { AdminDashboard } from './views/AdminDashboard';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<{ email: string; role: string } | null>(null);

  const handleLogin = (email: string, role: string) => {
    setCurrentUser({ email, role });
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  if (!currentUser) {
    return <AuthView onLogin={handleLogin} />;
  }

  if (currentUser.role === 'STUDENT') {
    return <StudentPortal userEmail={currentUser.email} onLogout={handleLogout} />;
  }

  if (currentUser.role === 'FACULTY') {
    return <FacultyDashboard userEmail={currentUser.email} onLogout={handleLogout} />;
  }

  if (currentUser.role === 'ADMIN') {
    return <AdminDashboard userEmail={currentUser.email} onLogout={handleLogout} />;
  }

  return <AuthView onLogin={handleLogin} />;
};

export default App;
