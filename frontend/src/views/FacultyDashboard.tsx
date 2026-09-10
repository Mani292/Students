import React, { useEffect, useState } from 'react';
import { Card, Button, Badge, StatCard, Modal, Alert, EmptyState, Avatar, LoadingSpinner } from '../components/UIComponents';
import { getPendingPermissions, updatePermission, type PermissionRequest } from '../api';
import {
  ShieldCheck, CheckCircle, XCircle, LogOut, FileText,
  Activity, GraduationCap, Calendar, Copy, RefreshCw, Clock,
} from 'lucide-react';

interface FacultyDashboardProps {
  userEmail: string;
  token: string;
  onLogout: () => void;
}

type FacultyTab = 'permissions' | 'attendance' | 'classes';

export const FacultyDashboard: React.FC<FacultyDashboardProps> = ({ userEmail, token, onLogout }) => {
  const [activeTab, setActiveTab] = useState<FacultyTab>('permissions');
  const [permissions, setPermissions] = useState<PermissionRequest[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Attendance session state
  const [sessionModalOpen, setSessionModalOpen] = useState(false);
  const [startingSession, setStartingSession] = useState(false);
  const [currentSession, setCurrentSession] = useState<{
    sessionToken: string;
    totpCode: string;
    courseCode: string;
    startedAt: Date;
    expiresAt: Date;
  } | null>(null);
  const [sessionCourse, setSessionCourse] = useState('CS301');
  const [copied, setCopied] = useState<'token' | 'totp' | null>(null);
  const [timeLeft, setTimeLeft] = useState(0);

  // Mock today's schedule
  const todayClasses = [
    { code: 'CS301', name: 'Database Systems', time: '10:00–11:30 AM', room: 'Room 301', students: 42 },
    { code: 'CS201', name: 'Operating Systems', time: '02:00–03:30 PM', room: 'Room 204', students: 38 },
    { code: 'CS401', name: 'Machine Learning Lab', time: '04:00–05:30 PM', room: 'Lab 101', students: 24 },
  ];

  useEffect(() => {
    getPendingPermissions(token)
      .then(setPermissions)
      .catch(err => setError(err instanceof Error ? err.message : 'Could not load permissions'))
      .finally(() => setLoading(false));
  }, [token]);

  // TOTP countdown timer
  useEffect(() => {
    if (!currentSession) return;
    const tick = () => {
      const left = Math.max(0, Math.round((currentSession.expiresAt.getTime() - Date.now()) / 1000));
      setTimeLeft(left);
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [currentSession]);

  const handlePermissionAction = async (id: number, action: 'APPROVE' | 'REJECT') => {
    try {
      const updated = await updatePermission(token, id, action);
      setPermissions(prev => prev.map(p => p.id === id ? updated : p));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed');
    }
  };

  const handleStartSession = async () => {
    setStartingSession(true);
    try {
      // Call backend to start session
      const res = await fetch(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'}/attendance/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ course_code: sessionCourse }),
      });

      let data: { session_token?: string; totp_code?: string } = {};
      if (res.ok) {
        data = await res.json();
      }

      // If backend returns data, use it; otherwise generate a demo token
      const now = new Date();
      const expires = new Date(now.getTime() + 30 * 1000); // 30s TOTP window
      setCurrentSession({
        sessionToken: data.session_token ?? `${sessionCourse}-${now.toISOString().slice(0, 10)}`,
        totpCode: data.totp_code ?? String(Math.floor(100000 + Math.random() * 900000)),
        courseCode: sessionCourse,
        startedAt: now,
        expiresAt: expires,
      });
      setSessionModalOpen(false);
    } catch {
      // Demo fallback
      const now = new Date();
      setCurrentSession({
        sessionToken: `${sessionCourse}-${now.toISOString().slice(0, 10)}`,
        totpCode: String(Math.floor(100000 + Math.random() * 900000)),
        courseCode: sessionCourse,
        startedAt: now,
        expiresAt: new Date(now.getTime() + 30000),
      });
      setSessionModalOpen(false);
    } finally {
      setStartingSession(false);
    }
  };

  const handleRefreshTotp = () => {
    if (!currentSession) return;
    const newCode = String(Math.floor(100000 + Math.random() * 900000));
    const now = new Date();
    setCurrentSession({ ...currentSession, totpCode: newCode, expiresAt: new Date(now.getTime() + 30000) });
  };

  const handleCopy = (type: 'token' | 'totp', value: string) => {
    navigator.clipboard.writeText(value).catch(() => {});
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  const pendingCount = permissions.filter(p => ['PENDING', 'FACULTY_REVIEW'].includes(p.status)).length;

  const navItems: { id: FacultyTab; label: string; icon: React.ElementType; badge?: number }[] = [
    { id: 'permissions', label: 'Leave Approvals',   icon: FileText,   badge: pendingCount || undefined },
    { id: 'attendance',  label: 'Attendance',         icon: ShieldCheck },
    { id: 'classes',     label: 'My Classes',         icon: Calendar },
  ];

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'hsl(var(--surface-1))' }}>

      {/* ===== TOPBAR ===== */}
      <header className="border-b px-5 py-3 flex items-center justify-between sticky top-0 z-40 glass"
              style={{ borderColor: 'hsl(var(--surface-border))' }}>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg">
            <GraduationCap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-[hsl(var(--text-primary))]">Faculty Dashboard</h1>
            <p className="text-[10px] text-[hsl(var(--text-muted))]">SmartUniv · Department of Computer Science</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="info" dot>Faculty</Badge>
          <Avatar name={userEmail} size="sm" />
          <Button variant="ghost" size="sm" onClick={onLogout}><LogOut className="h-4 w-4" /></Button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* ===== SIDEBAR ===== */}
        <aside className="w-52 border-r hidden md:flex flex-col p-3 gap-0.5"
               style={{ borderColor: 'hsl(var(--surface-border))', background: 'hsl(var(--surface-2))' }}>
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button key={item.id} onClick={() => setActiveTab(item.id)} className={`nav-item ${activeTab === item.id ? 'active' : ''}`}>
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span className="flex-1 text-left">{item.label}</span>
                {item.badge ? <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400">{item.badge}</span> : null}
              </button>
            );
          })}

          <div className="mt-auto pt-3 border-t border-white/5">
            <div className="px-3 py-2.5 rounded-xl bg-white/3">
              <p className="text-[10px] text-[hsl(var(--text-muted))]">Email</p>
              <p className="text-xs font-semibold text-[hsl(var(--text-primary))] truncate">{userEmail}</p>
            </div>
          </div>
        </aside>

        {/* ===== CONTENT ===== */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && <Alert type="danger" onClose={() => setError(null)}>{error}</Alert>}

          {/* Stat row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Pending Approvals" value={pendingCount} change="Leave requests" iconColor="from-amber-500 to-orange-600" icon={<FileText className="h-5 w-5" />} changeType={pendingCount > 0 ? 'negative' : 'positive'} />
            <StatCard label="Today's Classes" value={todayClasses.length} change="Scheduled sessions" iconColor="from-indigo-500 to-purple-600" icon={<Calendar className="h-5 w-5" />} changeType="neutral" />
            <StatCard label="Avg Attendance" value="88%" change="This semester" iconColor="from-emerald-500 to-teal-600" icon={<Activity className="h-5 w-5" />} changeType="positive" />
            <StatCard label="Session Active" value={currentSession ? '1' : '0'} change={currentSession ? `${currentSession.courseCode}` : 'None running'} iconColor="from-blue-500 to-indigo-600" icon={<ShieldCheck className="h-5 w-5" />} changeType={currentSession ? 'positive' : 'neutral'} />
          </div>

          {/* ─── PERMISSIONS TAB ─── */}
          {activeTab === 'permissions' && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Student Leave Requests</h2>
              {loading ? (
                <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
              ) : permissions.length === 0 ? (
                <Card>
                  <EmptyState
                    icon={<FileText className="w-10 h-10" />}
                    title="No pending approvals"
                    description="All student leave requests have been resolved."
                  />
                </Card>
              ) : (
                <Card title={`${pendingCount} request${pendingCount !== 1 ? 's' : ''} pending review`}>
                  <div className="divide-y divide-white/5 -mx-6 px-6 mt-2">
                    {permissions.map(p => (
                      <div key={p.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <Avatar name={p.student_name ?? 'Student'} size="sm" />
                            <div>
                              <p className="font-bold text-sm text-[hsl(var(--text-primary))]">{p.student_name ?? 'Student'}</p>
                              {p.student_roll_number && (
                                <span className="px-2 py-0.5 bg-indigo-500/15 text-indigo-400 font-mono font-bold text-[10px] rounded-lg border border-indigo-500/25">
                                  Roll: {p.student_roll_number}
                                </span>
                              )}
                            </div>
                          </div>
                          <p className="text-xs text-[hsl(var(--text-secondary))] mt-2 leading-relaxed">
                            <span className="font-medium text-[hsl(var(--text-primary))]">Reason:</span> {p.reason}
                          </p>
                          <p className="text-[10px] text-[hsl(var(--text-muted))] mt-1">
                            {new Date(p.start_date).toLocaleDateString()} → {new Date(p.end_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {['PENDING', 'FACULTY_REVIEW'].includes(p.status) ? (
                            <>
                              <Button variant="primary" size="sm" onClick={() => handlePermissionAction(p.id, 'APPROVE')}>
                                <CheckCircle className="h-3.5 w-3.5" /> Approve
                              </Button>
                              <Button variant="danger" size="sm" onClick={() => handlePermissionAction(p.id, 'REJECT')}>
                                <XCircle className="h-3.5 w-3.5" /> Reject
                              </Button>
                            </>
                          ) : (
                            <Badge variant={p.status === 'REJECTED' ? 'danger' : 'success'}>{p.status}</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </div>
          )}

          {/* ─── ATTENDANCE TAB ─── */}
          {activeTab === 'attendance' && (
            <div className="space-y-6 animate-fade-in max-w-2xl">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Smart Attendance Sessions</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Start a TOTP session — students scan the code to mark attendance</p>
              </div>

              {/* Active session display */}
              {currentSession && (
                <div className="rounded-2xl overflow-hidden shadow-2xl animate-fade-in-up"
                     style={{ background: 'linear-gradient(135deg, hsl(217,91%,18%), hsl(262,60%,20%))' }}>
                  <div className="px-6 pt-5 pb-3 border-b border-white/10 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="text-sm font-bold text-white">Session Active — {currentSession.courseCode}</span>
                    </div>
                    <Badge variant="success" dot>Live</Badge>
                  </div>

                  <div className="px-6 py-6 space-y-5">
                    {/* Session token */}
                    <div>
                      <p className="text-xs font-semibold text-white/60 uppercase tracking-wide mb-2">Session Token</p>
                      <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
                        <code className="text-white font-mono text-sm flex-1 select-all">{currentSession.sessionToken}</code>
                        <button onClick={() => handleCopy('token', currentSession.sessionToken)}
                                className="text-white/50 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/10">
                          {copied === 'token' ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>

                    {/* TOTP code */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs font-semibold text-white/60 uppercase tracking-wide">TOTP Code</p>
                        <div className="flex items-center gap-2 text-xs text-white/50">
                          <Clock className="w-3.5 h-3.5" />
                          Refreshes in {timeLeft}s
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
                        <code className="text-white font-mono text-4xl font-extrabold tracking-[0.3em] flex-1 text-center">
                          {currentSession.totpCode}
                        </code>
                      </div>
                      {/* Progress bar for expiry */}
                      <div className="mt-2 h-1.5 rounded-full overflow-hidden bg-white/10">
                        <div
                          className="h-full rounded-full transition-all duration-1000"
                          style={{
                            width: `${(timeLeft / 30) * 100}%`,
                            background: timeLeft > 10 ? '#10b981' : '#ef4444',
                          }}
                        />
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <Button variant="glass" size="sm" onClick={handleRefreshTotp} className="flex-1">
                        <RefreshCw className="w-3.5 h-3.5" /> Refresh TOTP
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => setCurrentSession(null)} className="flex-1">
                        <XCircle className="w-3.5 h-3.5" /> End Session
                      </Button>
                    </div>
                  </div>

                  <div className="px-6 py-3 border-t border-white/10 text-center">
                    <p className="text-xs text-white/40">Display this screen to students. They enter the session token + TOTP to mark attendance.</p>
                  </div>
                </div>
              )}

              {/* Start session button */}
              {!currentSession && (
                <Card title="Start New Attendance Session" glow>
                  <p className="text-sm text-[hsl(var(--text-secondary))] mb-4">
                    Select the course and start a session. A TOTP code will be generated that refreshes every 30 seconds.
                  </p>
                  <Button variant="primary" size="lg" className="w-full glow-primary" onClick={() => setSessionModalOpen(true)}>
                    <ShieldCheck className="h-5 w-5" /> Start Attendance Session
                  </Button>
                </Card>
              )}
            </div>
          )}

          {/* ─── CLASSES TAB ─── */}
          {activeTab === 'classes' && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Today's Schedule</h2>
              <div className="space-y-3">
                {todayClasses.map((cls, i) => (
                  <Card key={i}>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                          <Calendar className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-bold text-[hsl(var(--text-primary))]">{cls.code} — {cls.name}</p>
                          <p className="text-xs text-[hsl(var(--text-muted))] mt-0.5">{cls.room} · {cls.time} · {cls.students} students enrolled</p>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => { setSessionCourse(cls.code); setActiveTab('attendance'); setSessionModalOpen(true); }}
                      >
                        <ShieldCheck className="h-3.5 w-3.5" /> Start Session
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* ===== SESSION START MODAL ===== */}
      <Modal open={sessionModalOpen} onClose={() => setSessionModalOpen(false)} title="Start Attendance Session">
        <div className="space-y-4">
          <p className="text-sm text-[hsl(var(--text-secondary))]">
            Select the course for this attendance session. A TOTP code will be generated for students to verify.
          </p>
          <div>
            <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Course</label>
            <select value={sessionCourse} onChange={e => setSessionCourse(e.target.value)} className="dark-input">
              {todayClasses.map(cls => (
                <option key={cls.code} value={cls.code}>{cls.code} — {cls.name}</option>
              ))}
            </select>
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" className="flex-1" onClick={() => setSessionModalOpen(false)}>Cancel</Button>
            <Button variant="primary" className="flex-1 glow-primary" onClick={handleStartSession} loading={startingSession} disabled={startingSession}>
              <ShieldCheck className="h-4 w-4" /> Start Session
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
