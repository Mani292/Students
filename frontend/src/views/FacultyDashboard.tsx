import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, StatCard } from '../components/UIComponents';
import { ShieldCheck, QrCode, AlertTriangle, CheckCircle, XCircle, LogOut } from 'lucide-react';

interface FacultyDashboardProps {
  userEmail: string;
  onLogout: () => void;
}

export const FacultyDashboard: React.FC<FacultyDashboardProps> = ({ userEmail, onLogout }) => {
  const [sessionActive, setSessionActive] = useState(false);
  const [totpCode, setTotpCode] = useState('8F2A91');
  const [timeLeft, setTimeLeft] = useState(15);

  const [anomalies] = useState([
    { id: 1, studentName: 'Bob Mechanic (MECH002)', reason: 'Duplicate device fingerprint matching Alice (MECH001)', severity: 'HIGH', status: 'UNRESOLVED' }
  ]);

  const [permissions, setPermissions] = useState([
    { id: 101, studentName: 'Charlie Student', reason: 'Fever Medical Leave', dates: '2025-08-26 to 2025-08-28', status: 'PENDING' }
  ]);

  useEffect(() => {
    let timer: any;
    if (sessionActive) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            // Generate next TOTP
            const chars = '0123456789ABCDEF';
            let newTotp = '';
            for (let i = 0; i < 6; i++) newTotp += chars[Math.floor(Math.random() * chars.length)];
            setTotpCode(newTotp);
            return 15;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [sessionActive]);

  const handleApproveLeave = (id: number) => {
    setPermissions(prev => prev.map(p => p.id === id ? { ...p, status: 'APPROVED (FACULTY)' } : p));
  };

  const handleRejectLeave = (id: number) => {
    setPermissions(prev => prev.map(p => p.id === id ? { ...p, status: 'REJECTED' } : p));
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-slate-900 text-white border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-600 rounded-xl">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-base font-bold">Faculty Academic Dashboard</h1>
            <p className="text-xs text-slate-400">{userEmail} • Department of Computer Science</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="info">Faculty Workspace</Badge>
          <Button variant="ghost" size="sm" onClick={onLogout} className="text-slate-300 hover:text-white">
            <LogOut className="h-4 w-4 mr-1" /> Logout
          </Button>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard label="Today's Classes" value="3 Classes" change="Next: CS101 at 10:00 AM" icon={<ShieldCheck className="h-6 w-6" />} />
          <StatCard label="Anti-Proxy Anomalies" value={`${anomalies.filter(a => a.status === 'UNRESOLVED').length} Flagged`} change="Review required" icon={<AlertTriangle className="h-6 w-6" />} />
          <StatCard label="Pending Permissions" value={`${permissions.filter(p => p.status === 'PENDING').length} Requests`} change="Awaiting verification" icon={<CheckCircle className="h-6 w-6" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Smart Attendance Session Launcher */}
          <Card title="Smart Dynamic Attendance Launcher (CS101)" subtitle="Displays a dynamic 15-second rotating TOTP token to prevent proxy attendance screenshots.">
            {!sessionActive ? (
              <Button variant="primary" size="lg" onClick={() => setSessionActive(true)} className="w-full mt-4">
                <QrCode className="h-5 w-5 mr-2" /> Start 45-Min Attendance Session
              </Button>
            ) : (
              <div className="space-y-4 mt-2">
                <div className="p-6 bg-slate-900 text-white rounded-2xl flex flex-col items-center justify-center space-y-2">
                  <span className="text-xs text-slate-400 uppercase tracking-widest">Rotating Dynamic TOTP QR Code</span>
                  <div className="text-4xl font-mono font-extrabold text-sky-400 tracking-widest">{totpCode}</div>
                  <div className="text-xs text-slate-400">Regenerates in <span className="text-amber-400 font-bold">{timeLeft}s</span></div>
                </div>
                <Button variant="danger" className="w-full" onClick={() => setSessionActive(false)}>
                  Close Attendance Session
                </Button>
              </div>
            )}
          </Card>

          {/* Anti-Proxy Anomaly Reviewer */}
          <Card title="Anti-Proxy Anomaly Detection Log" subtitle="AI & Session fingerprinting flagged suspicious student attendance patterns.">
            <div className="space-y-3 mt-2">
              {anomalies.map(a => (
                <div key={a.id} className="p-3 border border-amber-200 bg-amber-50 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm text-slate-900">{a.studentName}</span>
                    <Badge variant="danger">{a.severity} SEVERITY</Badge>
                  </div>
                  <p className="text-xs text-amber-900">{a.reason}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Leave Permissions Approval Center */}
        <Card title="Student Leave & Permission Requests">
          <div className="divide-y divide-slate-200">
            {permissions.map(p => (
              <div key={p.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm text-slate-900">{p.studentName}</p>
                  <p className="text-xs text-slate-500">{p.reason} • ({p.dates})</p>
                </div>
                <div className="flex items-center space-x-2">
                  {p.status === 'PENDING' ? (
                    <>
                      <Button variant="primary" size="sm" onClick={() => handleApproveLeave(p.id)}>
                        <CheckCircle className="h-4 w-4 mr-1" /> Approve
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleRejectLeave(p.id)}>
                        <XCircle className="h-4 w-4 mr-1" /> Reject
                      </Button>
                    </>
                  ) : (
                    <Badge variant={p.status.includes('APPROVED') ? 'success' : 'danger'}>{p.status}</Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </main>
    </div>
  );
};
