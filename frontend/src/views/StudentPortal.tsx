import React, { useEffect, useRef, useState } from 'react';
import {
  Card, Button, Badge, StatCard, ProgressBar, Avatar,
  EmptyState, Alert, TypingIndicator, LoadingSpinner,
} from '../components/UIComponents';
import {
  applyPermission, createService, generateLearningPath, generateProjectMentor,
  getAcademicProfile, getJobs, getMyPermissions, getMyServices,
  getNotifications, markNotificationRead, matchJob, sendAIMessage,
  type AcademicProfile, type Job, type JobMatch, type LearningPath,
  type Notification, type PermissionRequest, type ServiceRequest, getDigitalId,
} from '../api';
import {
  LayoutDashboard, FileText, Award, Bot, BookOpen, Briefcase, Code,
  User, LogOut, Send, Bell, CheckCircle, XCircle, ChevronRight,
  Fingerprint, Zap, Target, TrendingUp, GraduationCap, Shield,
  Star, BookMarked,
} from 'lucide-react';

interface StudentPortalProps {
  userEmail: string;
  token: string;
  onLogout: () => void;
}

type TabId = 'overview' | 'grades' | 'permissions' | 'services' | 'copilot' | 'learning' | 'career' | 'project_lab' | 'attendance' | 'digital_id';

const NAV_ITEMS: { id: TabId; label: string; icon: React.ElementType; badge?: number }[] = [
  { id: 'overview',    label: 'Overview',        icon: LayoutDashboard },
  { id: 'grades',      label: 'Grade Book',       icon: BookMarked },
  { id: 'permissions', label: 'Leave & Permissions', icon: FileText },
  { id: 'attendance',  label: 'Attendance',       icon: Shield },
  { id: 'services',    label: 'Service Center',   icon: Award },
  { id: 'digital_id',  label: 'Digital ID',       icon: Fingerprint },
  { id: 'copilot',     label: 'AI Copilot',       icon: Bot },
  { id: 'learning',    label: 'Learning Hub',     icon: BookOpen },
  { id: 'career',      label: 'Career Matching',  icon: Briefcase },
  { id: 'project_lab', label: 'Project Lab',      icon: Code },
];

export const StudentPortal: React.FC<StudentPortalProps> = ({ userEmail, token, onLogout }) => {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  // ── Data state ──
  const [profile, setProfile] = useState<AcademicProfile | null>(null);
  const [permissions, setPermissions] = useState<PermissionRequest[]>([]);
  const [services, setServices] = useState<ServiceRequest[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [digitalId, setDigitalId] = useState<Record<string, string | number> | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);

  // ── UI state ──
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const notifPanelRef = useRef<HTMLDivElement>(null);

  // ── Form state ──
  const [leaveReason, setLeaveReason] = useState('');
  const [leaveSubmitted, setLeaveSubmitted] = useState(false);
  const [leaveLoading, setLeaveLoading] = useState(false);
  const [serviceType, setServiceType] = useState('BONAFIDE');
  const [serviceSubmitted, setServiceSubmitted] = useState(false);
  const [serviceLoading, setServiceLoading] = useState(false);

  // ── Attendance ──
  const [sessionToken, setSessionToken] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [attendanceMsg, setAttendanceMsg] = useState<{ type: 'success' | 'danger'; text: string } | null>(null);
  const [attendanceLoading, setAttendanceLoading] = useState(false);

  // ── AI Chat ──
  const [messages, setMessages] = useState<{ sender: 'user' | 'ai'; text: string; tools?: string[]; ts: Date }[]>([
    { sender: 'ai', text: 'Hi! I\'m your SmartUniv AI Copilot 🤖 Ask me anything about attendance policies, your grades, career paths, or university services.', ts: new Date() },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [aiTyping, setAiTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // ── Career ──
  const [jobMatch, setJobMatch] = useState<JobMatch | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobMatchLoading, setJobMatchLoading] = useState(false);

  // ── Learning ──
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [learningSubject, setLearningSubject] = useState('Machine Learning');
  const [learningLoading, setLearningLoading] = useState(false);

  // ── Project ──
  const [projectIdea, setProjectIdea] = useState('AI Traffic Management System');
  const [projectOutput, setProjectOutput] = useState<any>(null);
  const [projectLoading, setProjectLoading] = useState(false);

  // ── Initial data load ──
  useEffect(() => {
    Promise.all([
      getMyPermissions(token),
      getMyServices(token),
      getAcademicProfile(token),
      getNotifications(token),
      getJobs(),
      getDigitalId(token),
    ])
      .then(([perm, svc, prof, notif, j, did]) => {
        setPermissions(perm);
        setServices(svc);
        setProfile(prof);
        setNotifications(notif);
        setJobs(j);
        setDigitalId(did);
      })
      .catch(err => setLoadError(err instanceof Error ? err.message : 'Could not load data'))
      .finally(() => setInitialLoading(false));
  }, [token]);

  // ── Auto-scroll chat ──
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, aiTyping]);

  // ── Close notif panel on outside click ──
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifPanelRef.current && !notifPanelRef.current.contains(e.target as Node)) {
        setShowNotifPanel(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  // ── Handlers ──
  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const msg = chatInput.trim();
    setMessages(prev => [...prev, { sender: 'user', text: msg, ts: new Date() }]);
    setChatInput('');
    setAiTyping(true);
    try {
      const result = await sendAIMessage(token, msg, conversationId);
      setConversationId(result.conversation_id);
      setMessages(prev => [...prev, { sender: 'ai', text: result.response, tools: result.tools_used, ts: new Date() }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'ai', text: err instanceof Error ? err.message : 'AI request failed', ts: new Date() }]);
    } finally {
      setAiTyping(false);
    }
  };

  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLeaveLoading(true);
    try {
      const p = await applyPermission(token, leaveReason);
      setPermissions(prev => [p, ...prev]);
      setLeaveReason('');
      setLeaveSubmitted(true);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Permission request failed');
    } finally {
      setLeaveLoading(false);
    }
  };

  const handleCreateService = async () => {
    setServiceLoading(true);
    try {
      const s = await createService(token, serviceType);
      setServices(prev => [s, ...prev]);
      setServiceSubmitted(true);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Service request failed');
    } finally {
      setServiceLoading(false);
    }
  };

  const handleRecordAttendance = async (e: React.FormEvent) => {
    e.preventDefault();
    setAttendanceLoading(true);
    setAttendanceMsg(null);
    try {
      const deviceFingerprint = navigator.userAgent;
      const { recordAttendance } = await import('../api');
      await recordAttendance(token, sessionToken, totpCode, deviceFingerprint);
      setAttendanceMsg({ type: 'success', text: '✅ Attendance recorded successfully!' });
      setSessionToken(''); setTotpCode('');
    } catch (err) {
      setAttendanceMsg({ type: 'danger', text: err instanceof Error ? err.message : 'Attendance failed' });
    } finally {
      setAttendanceLoading(false);
    }
  };

  const handleMatchJob = async (job: Job) => {
    setSelectedJob(job);
    setJobMatchLoading(true);
    try {
      const match = await matchJob(`${job.title} ${job.required_skills.join(' ')}`, profile?.skills ?? []);
      setJobMatch(match);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Job match failed');
    } finally {
      setJobMatchLoading(false);
    }
  };

  const handleGenerateLearning = async () => {
    setLearningLoading(true);
    try {
      setLearningPath(await generateLearningPath(token, learningSubject, 'Software Engineer'));
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Learning path failed');
    } finally {
      setLearningLoading(false);
    }
  };

  const handleGenerateProject = async () => {
    setProjectLoading(true);
    try {
      setProjectOutput(await generateProjectMentor(token, projectIdea));
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Project mentor failed');
    } finally {
      setProjectLoading(false);
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      const updated = await markNotificationRead(token, id);
      setNotifications(prev => prev.map(n => n.id === updated.id ? updated : n));
    } catch { /* silent */ }
  };

  // ── Mock grades data (based on profile) ──
  const grades = profile ? [
    { code: 'CS101', name: 'Data Structures', credits: 4, grade: 'A', points: 10, semester: profile.semester },
    { code: 'CS201', name: 'Operating Systems', credits: 4, grade: 'B+', points: 9, semester: profile.semester },
    { code: 'CS301', name: 'Database Systems', credits: 3, grade: 'A+', points: 10, semester: profile.semester },
    { code: 'CS401', name: 'Machine Learning', credits: 3, grade: 'A', points: 10, semester: profile.semester },
    { code: 'CS501', name: 'Computer Networks', credits: 4, grade: 'B', points: 8, semester: profile.semester },
    { code: 'MA101', name: 'Engineering Mathematics', credits: 4, grade: 'A', points: 10, semester: profile.semester },
  ] : [];

  const gradeColorMap: Record<string, string> = {
    'A+': 'success', 'A': 'success', 'B+': 'info', 'B': 'info', 'C': 'warning', 'F': 'danger',
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'hsl(var(--surface-1))' }}>
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-3 text-sm text-[hsl(var(--text-muted))]">Loading your portal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'hsl(var(--surface-1))' }}>

      {/* ===== TOPBAR ===== */}
      <header className="border-b px-5 py-3 flex items-center justify-between sticky top-0 z-40 glass"
              style={{ borderColor: 'hsl(var(--surface-border))' }}>
        {/* Left: Logo */}
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
            <GraduationCap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-[hsl(var(--text-primary))]">Student Portal</h1>
            <p className="text-[10px] text-[hsl(var(--text-muted))]">SmartUniv AI Platform</p>
          </div>
        </div>

        {/* Right: actions */}
        <div className="flex items-center gap-3">
          <Badge variant="success" dot>Active Session</Badge>

          {/* Notification Bell */}
          <div className="relative" ref={notifPanelRef}>
            <button
              onClick={() => setShowNotifPanel(v => !v)}
              className="relative p-2 rounded-xl text-[hsl(var(--text-secondary))] hover:bg-white/5 hover:text-[hsl(var(--text-primary))] transition-all"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="notif-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
              )}
            </button>

            {/* Notification dropdown */}
            {showNotifPanel && (
              <div className="absolute right-0 top-12 w-80 glass rounded-2xl shadow-2xl border-white/10 z-50 overflow-hidden animate-fade-in-up">
                <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
                  <span className="text-sm font-semibold text-[hsl(var(--text-primary))]">Notifications</span>
                  {unreadCount > 0 && <Badge variant="info" size="sm">{unreadCount} unread</Badge>}
                </div>
                <div className="max-h-72 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <p className="p-4 text-xs text-center text-[hsl(var(--text-muted))]">No notifications</p>
                  ) : notifications.slice(0, 8).map(n => (
                    <div key={n.id} className={`px-4 py-3 border-b border-white/5 hover:bg-white/3 transition-colors ${!n.is_read ? 'bg-indigo-500/5' : ''}`}>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          {!n.is_read && <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block mr-1.5 mb-0.5" />}
                          <p className="text-xs font-semibold text-[hsl(var(--text-primary))] truncate">{n.title}</p>
                          <p className="text-[11px] text-[hsl(var(--text-muted))] mt-0.5 line-clamp-2">{n.message}</p>
                        </div>
                        {!n.is_read && (
                          <button onClick={() => handleMarkRead(n.id)} className="text-[10px] text-indigo-400 hover:text-indigo-300 whitespace-nowrap mt-0.5">Mark read</button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Avatar + name */}
          <div className="flex items-center gap-2 pl-2 border-l border-white/10">
            <Avatar name={profile?.full_name ?? userEmail} size="sm" />
            <div className="hidden sm:block">
              <p className="text-xs font-semibold text-[hsl(var(--text-primary))] leading-tight">{profile?.full_name ?? userEmail}</p>
              <p className="text-[10px] text-[hsl(var(--text-muted))] leading-tight">{profile?.roll_number ?? 'Student'}</p>
            </div>
          </div>

          <Button variant="ghost" size="sm" onClick={onLogout} className="gap-1.5">
            <LogOut className="h-4 w-4" /> <span className="hidden sm:inline">Logout</span>
          </Button>
        </div>
      </header>

      {/* ===== BODY ===== */}
      <div className="flex-1 flex overflow-hidden">

        {/* ===== SIDEBAR ===== */}
        <aside className="w-56 border-r hidden md:flex flex-col p-3 gap-0.5"
               style={{ borderColor: 'hsl(var(--surface-border))', background: 'hsl(var(--surface-2))' }}>
          {NAV_ITEMS.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span className="flex-1 text-left">{item.label}</span>
                {item.id === 'copilot' && <Zap className="h-3 w-3 text-indigo-400 opacity-60" />}
              </button>
            );
          })}

          {/* Profile card at bottom */}
          <div className="mt-auto pt-3 border-t border-white/5">
            <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-white/3">
              <Avatar name={profile?.full_name ?? userEmail} size="sm" />
              <div className="min-w-0">
                <p className="text-xs font-semibold text-[hsl(var(--text-primary))] truncate">{profile?.department ?? 'Department'}</p>
                <p className="text-[10px] text-[hsl(var(--text-muted))]">Year {profile?.year ?? '—'} · Sem {profile?.semester ?? '—'}</p>
              </div>
            </div>
          </div>
        </aside>

        {/* ===== CONTENT ===== */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {loadError && (
            <Alert type="danger" onClose={() => setLoadError(null)}>{loadError}</Alert>
          )}

          {/* ─────── OVERVIEW ─────── */}
          {activeTab === 'overview' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Welcome back, {profile?.full_name?.split(' ')[0] ?? 'Student'} 👋</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Here's your academic snapshot for Semester {profile?.semester}</p>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard label="CGPA" value={profile?.cgpa ?? '—'} change={profile?.department} iconColor="from-blue-500 to-indigo-600" icon={<GraduationCap className="h-5 w-5" />} />
                <StatCard label="Pending Leave" value={`${permissions.filter(p => !['APPROVED','REJECTED'].includes(p.status)).length}`} change="Requests" iconColor="from-amber-500 to-orange-600" icon={<FileText className="h-5 w-5" />} changeType="neutral" />
                <StatCard label="Active Roadmap" value="Python ML" change="Step 2 of 5" iconColor="from-emerald-500 to-teal-600" icon={<BookOpen className="h-5 w-5" />} changeType="positive" />
                <StatCard label="AI Sessions" value={conversationId ? conversationId : '0'} change="Conversations" iconColor="from-purple-500 to-indigo-600" icon={<Bot className="h-5 w-5" />} changeType="neutral" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Academic performance */}
                <Card title="Academic Performance" className="lg:col-span-2">
                  <div className="space-y-4 mt-2">
                    <ProgressBar value={profile?.cgpa ? Math.round((profile.cgpa / 10) * 100) : 82} label="CGPA Score" color="var(--gradient-primary)" />
                    <ProgressBar value={88} label="Attendance Rate" color="linear-gradient(135deg, #10b981, #059669)" />
                    <ProgressBar value={72} label="Assignment Completion" color="linear-gradient(135deg, #f59e0b, #d97706)" />
                    <ProgressBar value={profile?.skills?.length ? Math.min(100, profile.skills.length * 12) : 60} label="Skill Passport" color="linear-gradient(135deg, #8b5cf6, #6d28d9)" />
                  </div>
                </Card>

                {/* Notifications */}
                <Card title="Recent Notifications" action={
                  <Button variant="ghost" size="xs" onClick={() => setShowNotifPanel(true)}>View all</Button>
                }>
                  <div className="space-y-2 mt-1">
                    {notifications.length === 0 ? (
                      <EmptyState icon={<Bell className="w-8 h-8" />} title="No notifications" description="You're all caught up!" />
                    ) : notifications.slice(0, 4).map(n => (
                      <div key={n.id} className={`p-2.5 rounded-lg border text-xs transition-all ${!n.is_read ? 'border-indigo-500/25 bg-indigo-500/5' : 'border-white/5 bg-white/2'}`}>
                        {!n.is_read && <span className="inline-block w-1.5 h-1.5 rounded-full bg-indigo-400 mr-1.5 mb-0.5" />}
                        <span className="font-semibold text-[hsl(var(--text-primary))]">{n.title}</span>
                        <p className="text-[hsl(var(--text-muted))] mt-0.5 truncate">{n.message}</p>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* AI Insights */}
                <Card title="AI Career Insights" className="lg:col-span-2">
                  <div className="space-y-3 mt-1">
                    <div className="p-3.5 rounded-xl border border-indigo-500/20 bg-indigo-500/5">
                      <div className="flex items-center gap-2 mb-1">
                        <Zap className="w-3.5 h-3.5 text-indigo-400" />
                        <p className="text-xs font-semibold text-indigo-300">Learning Opportunity</p>
                      </div>
                      <p className="text-xs text-[hsl(var(--text-secondary))]">
                        Based on your skills ({profile?.skills?.slice(0, 3).join(', ') ?? 'Python, FastAPI'}), completing the 'Docker Basics' module will boost your ATS match score by 18%.
                      </p>
                    </div>
                    <div className="p-3.5 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
                      <div className="flex items-center gap-2 mb-1">
                        <Target className="w-3.5 h-3.5 text-emerald-400" />
                        <p className="text-xs font-semibold text-emerald-300">Job Recommendation</p>
                      </div>
                      <p className="text-xs text-[hsl(var(--text-secondary))]">
                        {jobs[0] ? `${jobs[0].title} at ${jobs[0].company}` : 'Full-Stack Intern at TechCorp'} — matching {profile?.skills?.length ? `${Math.min(100, profile.skills.length * 14)}%` : '85%'} of your skill profile.
                      </p>
                    </div>
                    <div className="p-3.5 rounded-xl border border-amber-500/20 bg-amber-500/5">
                      <div className="flex items-center gap-2 mb-1">
                        <TrendingUp className="w-3.5 h-3.5 text-amber-400" />
                        <p className="text-xs font-semibold text-amber-300">Upcoming Deadlines</p>
                      </div>
                      <p className="text-xs text-[hsl(var(--text-secondary))]">
                        Mid-semester exams in 12 days. Your weakest subject based on grades: Operating Systems (B+).
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Upcoming classes */}
                <Card title="Today's Schedule">
                  <div className="space-y-2.5 mt-1">
                    {[
                      { code: 'CS301', name: 'Database Systems', room: 'Room 301', time: '10:00–11:30 AM', status: 'now' },
                      { code: 'CS201', name: 'Operating Systems', room: 'Room 204', time: '02:00–03:30 PM', status: 'upcoming' },
                      { code: 'CS401', name: 'Machine Learning', room: 'Lab 101', time: '04:00–05:00 PM', status: 'upcoming' },
                    ].map((cls, i) => (
                      <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg border border-white/5 hover:border-white/10 transition-all">
                        <div className={`w-1 self-stretch rounded-full ${cls.status === 'now' ? 'bg-emerald-400' : 'bg-indigo-400/40'}`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-semibold text-[hsl(var(--text-primary))] truncate">{cls.code} — {cls.name}</p>
                          <p className="text-[10px] text-[hsl(var(--text-muted))]">{cls.room} · {cls.time}</p>
                        </div>
                        <Badge variant={cls.status === 'now' ? 'success' : 'neutral'} dot={cls.status === 'now'}>{cls.status === 'now' ? 'Now' : 'Soon'}</Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* ─────── GRADES ─────── */}
          {activeTab === 'grades' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Grade Book</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Semester {profile?.semester} — {profile?.department}</p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Cumulative GPA" value={profile?.cgpa ?? '—'} change="out of 10.0" iconColor="from-blue-500 to-indigo-600" icon={<Star className="h-5 w-5" />} />
                <StatCard label="Total Credits" value={grades.reduce((a, g) => a + g.credits, 0)} change="this semester" iconColor="from-emerald-500 to-teal-600" icon={<BookMarked className="h-5 w-5" />} changeType="positive" />
                <StatCard label="Best Subject" value="DBMS" change="A+ · 10 points" iconColor="from-amber-500 to-orange-500" icon={<Award className="h-5 w-5" />} changeType="positive" />
                <StatCard label="Improvement" value="OS" change="B+ → target A" iconColor="from-rose-500 to-pink-600" icon={<TrendingUp className="h-5 w-5" />} changeType="negative" />
              </div>

              <Card title="Course Grades" subtitle="Current semester academic record">
                <div className="overflow-x-auto mt-2">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Course</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Credits</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Grade</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Points</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Performance</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {grades.map(g => (
                        <tr key={g.code} className="hover:bg-white/2 transition-colors">
                          <td className="py-3 px-3">
                            <p className="font-semibold text-[hsl(var(--text-primary))] text-xs">{g.code}</p>
                            <p className="text-[hsl(var(--text-muted))] text-[11px]">{g.name}</p>
                          </td>
                          <td className="py-3 px-3 text-xs text-[hsl(var(--text-secondary))]">{g.credits}</td>
                          <td className="py-3 px-3">
                            <Badge variant={(gradeColorMap[g.grade] ?? 'neutral') as any}>{g.grade}</Badge>
                          </td>
                          <td className="py-3 px-3 text-xs font-bold text-[hsl(var(--text-primary))]">{g.points}.0</td>
                          <td className="py-3 px-3 w-36">
                            <ProgressBar value={g.points * 10} showValue={false} height={5} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}

          {/* ─────── PERMISSIONS ─────── */}
          {activeTab === 'permissions' && (
            <div className="space-y-6 max-w-2xl animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Leave & Permissions</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Submit leave requests and track approval status</p>
              </div>
              <Card title="Apply for Leave">
                {leaveSubmitted && (
                  <Alert type="success" onClose={() => setLeaveSubmitted(false)}>
                    Leave request submitted! Your HOD has been notified. 🎉
                  </Alert>
                )}
                <form onSubmit={handleApplyLeave} className="space-y-4 mt-4">
                  <div>
                    <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Reason for Leave</label>
                    <textarea
                      required
                      rows={3}
                      value={leaveReason}
                      onChange={e => setLeaveReason(e.target.value)}
                      placeholder="Describe your reason (medical, personal, event...)..."
                      className="dark-input"
                    />
                  </div>
                  <Button type="submit" variant="primary" className="w-full" loading={leaveLoading} disabled={leaveLoading}>
                    Submit Leave Request
                  </Button>
                </form>

                <div className="mt-6 space-y-2">
                  <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Your Requests</p>
                  {permissions.length === 0 ? (
                    <EmptyState icon={<FileText className="w-8 h-8" />} title="No requests yet" description="Submit your first leave request above." />
                  ) : permissions.map(p => (
                    <div key={p.id} className="flex items-center justify-between p-3 rounded-lg border border-white/5 hover:border-white/10 transition-all text-sm">
                      <div>
                        <p className="text-[hsl(var(--text-primary))] text-xs font-medium truncate max-w-xs">{p.reason}</p>
                        <p className="text-[10px] text-[hsl(var(--text-muted))] mt-0.5">{new Date(p.created_at).toLocaleDateString()}</p>
                      </div>
                      <Badge variant={p.status === 'APPROVED' ? 'success' : p.status === 'REJECTED' ? 'danger' : 'warning'}>
                        {p.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* ─────── ATTENDANCE ─────── */}
          {activeTab === 'attendance' && (
            <div className="space-y-6 max-w-lg animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Mark Attendance</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Enter the session token and TOTP code from your faculty</p>
              </div>
              <Card title="Smart TOTP Attendance" glow>
                {attendanceMsg && (
                  <Alert type={attendanceMsg.type} onClose={() => setAttendanceMsg(null)}>
                    {attendanceMsg.text}
                  </Alert>
                )}
                <form onSubmit={handleRecordAttendance} className="space-y-4 mt-4">
                  <div>
                    <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Session Token</label>
                    <input
                      required
                      value={sessionToken}
                      onChange={e => setSessionToken(e.target.value)}
                      className="dark-input font-mono"
                      placeholder="e.g. CS301-2024-09-09"
                    />
                    <p className="text-[10px] text-[hsl(var(--text-muted))] mt-1">Get this from your faculty on the board/screen</p>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">TOTP Code</label>
                    <input
                      required
                      value={totpCode}
                      onChange={e => setTotpCode(e.target.value)}
                      className="dark-input font-mono tracking-[0.25em] text-lg text-center"
                      placeholder="• • • • • •"
                      maxLength={6}
                    />
                    <p className="text-[10px] text-[hsl(var(--text-muted))] mt-1">6-digit rotating code, changes every 30 seconds</p>
                  </div>
                  <Button type="submit" variant="primary" className="w-full glow-primary" loading={attendanceLoading} disabled={attendanceLoading}>
                    <Shield className="h-4 w-4" /> Submit Secure Attendance
                  </Button>
                </form>
                <div className="mt-4 p-3 rounded-xl bg-white/3 border border-white/5">
                  <p className="text-xs text-[hsl(var(--text-muted))] flex items-center gap-2">
                    <Shield className="h-3.5 w-3.5 text-emerald-400" />
                    Anti-spoofing enabled: device fingerprint + TOTP verification + anomaly detection active.
                  </p>
                </div>
              </Card>
            </div>
          )}

          {/* ─────── SERVICES ─────── */}
          {activeTab === 'services' && (
            <div className="space-y-6 max-w-2xl animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Service Center</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Request certificates, ID cards, and campus services</p>
              </div>
              <Card title="Request a Service">
                {serviceSubmitted && (
                  <Alert type="success" onClose={() => setServiceSubmitted(false)}>
                    Service request created! You'll be notified when it's processed.
                  </Alert>
                )}
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Service Type</label>
                    <select value={serviceType} onChange={e => setServiceType(e.target.value)} className="dark-input">
                      <option value="BONAFIDE">Bonafide Certificate</option>
                      <option value="ID_CARD">Replacement ID Card</option>
                      <option value="HOSTEL">Hostel Allocation Request</option>
                      <option value="TRANSPORT">Transport Bus Pass</option>
                      <option value="TRANSCRIPT">Official Transcript</option>
                      <option value="MIGRATION">Migration Certificate</option>
                    </select>
                  </div>
                  <Button variant="primary" className="w-full" onClick={handleCreateService} loading={serviceLoading} disabled={serviceLoading}>
                    Submit Request
                  </Button>
                </div>

                <div className="mt-6 space-y-2">
                  <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">My Requests</p>
                  {services.length === 0 ? (
                    <EmptyState icon={<Award className="w-8 h-8" />} title="No service requests yet" />
                  ) : services.map(s => (
                    <div key={s.id} className="flex items-center justify-between p-3 rounded-lg border border-white/5 hover:border-white/10 transition-all">
                      <div>
                        <p className="text-xs font-semibold text-[hsl(var(--text-primary))]">{s.service_type}</p>
                        <p className="text-[10px] text-[hsl(var(--text-muted))] mt-0.5">{new Date(s.created_at).toLocaleDateString()}</p>
                      </div>
                      <Badge variant={s.status === 'COMPLETED' ? 'success' : s.status === 'REJECTED' ? 'danger' : 'warning'}>{s.status}</Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* ─────── DIGITAL ID ─────── */}
          {activeTab === 'digital_id' && (
            <div className="space-y-6 max-w-sm animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Digital ID Card</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Your official university identity</p>
              </div>

              {digitalId ? (
                <div className="rounded-2xl overflow-hidden shadow-2xl"
                     style={{ background: 'var(--gradient-primary)', boxShadow: 'var(--shadow-glow)' }}>
                  {/* Card header */}
                  <div className="px-6 pt-6 pb-4 border-b border-white/20 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <GraduationCap className="w-5 h-5 text-white/80" />
                      <span className="text-white font-bold text-sm">SmartUniv</span>
                    </div>
                    <Badge variant="neutral" size="sm">STUDENT ID</Badge>
                  </div>

                  {/* Card body */}
                  <div className="px-6 py-6 text-center">
                    <div className="w-20 h-20 mx-auto rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center mb-4 ring-4 ring-white/20 shadow-xl">
                      <User className="h-10 w-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-extrabold text-white">{digitalId.full_name ?? 'N/A'}</h3>
                    <p className="text-white/70 font-mono text-sm mt-1">{digitalId.roll_number ?? 'N/A'}</p>

                    <div className="mt-5 grid grid-cols-2 gap-3">
                      {[
                        { label: 'Department', value: digitalId.department },
                        { label: 'Year', value: `Year ${profile?.year ?? '—'}` },
                        { label: 'Semester', value: `Sem ${profile?.semester ?? '—'}` },
                        { label: 'Status', value: 'Active' },
                      ].map((item, i) => (
                        <div key={i} className="bg-white/10 rounded-xl p-2.5 text-center">
                          <p className="text-[10px] text-white/60 uppercase tracking-wide">{item.label}</p>
                          <p className="text-white font-bold text-sm mt-0.5">{String(item.value ?? '—')}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Card footer */}
                  <div className="px-6 pb-5 text-center">
                    <p className="text-white/40 text-[10px]">Valid until: May 2026 · University of Technology</p>
                  </div>
                </div>
              ) : (
                <Card>
                  <EmptyState icon={<Fingerprint className="w-10 h-10" />} title="Loading Digital ID..." description="Fetching your identity from the university system." />
                </Card>
              )}
            </div>
          )}

          {/* ─────── AI COPILOT ─────── */}
          {activeTab === 'copilot' && (
            <div className="animate-fade-in h-[calc(100vh-120px)] flex flex-col">
              {/* Chat header */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-[hsl(var(--text-primary))] flex items-center gap-2">
                    <Bot className="h-5 w-5 text-indigo-400" /> AI Copilot
                  </h2>
                  <p className="text-sm text-[hsl(var(--text-muted))]">RAG-powered university assistant</p>
                </div>
                <Badge variant="info" dot>Active</Badge>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-2">
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'} gap-3`}>
                    {m.sender === 'ai' && (
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-1">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div className={`max-w-lg rounded-2xl px-4 py-3 text-sm ${m.sender === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white'
                      : 'bg-[hsl(var(--surface-3))] text-[hsl(var(--text-primary))] border border-white/5'
                    }`}>
                      <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                      {m.tools && m.tools.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-white/10 flex flex-wrap gap-1">
                          {m.tools.map((t, j) => (
                            <span key={j} className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/60">🔧 {t}</span>
                          ))}
                        </div>
                      )}
                      <p className={`text-[10px] mt-1.5 ${m.sender === 'user' ? 'text-white/50' : 'text-[hsl(var(--text-muted))]'}`}>
                        {m.ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    {m.sender === 'user' && <Avatar name={profile?.full_name ?? userEmail} size="sm" />}
                  </div>
                ))}
                {aiTyping && (
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <TypingIndicator />
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input */}
              <div className="flex items-center gap-3 mt-4 pt-4 border-t border-white/10">
                {/* Quick prompts */}
                <div className="flex-1 space-y-2">
                  <div className="flex gap-2 overflow-x-auto pb-1">
                    {['What is the attendance policy?', 'Show my CGPA', 'Best job for Python dev?', 'How to apply for leave?'].map((q, i) => (
                      <button key={i} onClick={() => setChatInput(q)} className="text-[10px] px-2.5 py-1.5 rounded-full border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 whitespace-nowrap transition-all">
                        {q}
                      </button>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Ask anything about your university..."
                      value={chatInput}
                      onChange={e => setChatInput(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                      className="dark-input flex-1"
                    />
                    <Button variant="primary" onClick={handleSendMessage} disabled={aiTyping || !chatInput.trim()} className="glow-primary">
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ─────── LEARNING HUB ─────── */}
          {activeTab === 'learning' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">AI Learning Hub</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Personalised roadmaps generated by AI for any skill or subject</p>
              </div>
              <Card title="Generate AI Roadmap">
                <div className="flex gap-3 mt-4">
                  <input
                    value={learningSubject}
                    onChange={e => setLearningSubject(e.target.value)}
                    className="dark-input flex-1"
                    placeholder="e.g. Machine Learning, System Design, React..."
                  />
                  <Button onClick={handleGenerateLearning} loading={learningLoading} disabled={learningLoading}>
                    <Zap className="h-4 w-4" /> Generate
                  </Button>
                </div>

                {!learningPath && !learningLoading && (
                  <EmptyState
                    icon={<BookOpen className="w-10 h-10" />}
                    title="Enter a subject above"
                    description="AI will generate a step-by-step learning roadmap tailored to your goals."
                  />
                )}

                {learningPath && (
                  <div className="mt-6 space-y-4">
                    <h4 className="font-bold text-[hsl(var(--text-primary))]">{learningPath.subject} Roadmap</h4>
                    <div className="relative">
                      {/* Timeline connector */}
                      <div className="absolute left-4 top-5 bottom-5 w-0.5 bg-gradient-to-b from-indigo-500 to-purple-600 opacity-30" />
                      <div className="space-y-4">
                        {learningPath.roadmap.map((step, i) => (
                          <div key={i} className="flex gap-4 relative">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-lg z-10">
                              {step.step}
                            </div>
                            <div className="flex-1 p-3.5 rounded-xl border border-white/5 hover:border-indigo-500/25 transition-all bg-white/2">
                              <p className="font-semibold text-sm text-[hsl(var(--text-primary))]">{step.title}</p>
                              <p className="text-xs text-[hsl(var(--text-secondary))] mt-1 leading-relaxed">{step.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {learningPath.recommended_resources?.length > 0 && (
                      <div className="mt-4">
                        <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide mb-2">Recommended Resources</p>
                        <div className="space-y-2">
                          {learningPath.recommended_resources.map((res, i) => (
                            <a key={i} href={res.url} target="_blank" rel="noopener noreferrer"
                               className="flex items-center gap-3 p-2.5 rounded-lg border border-white/5 hover:border-indigo-500/25 text-xs transition-all group">
                              <span className="px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-400 font-mono text-[10px]">{res.type}</span>
                              <span className="text-[hsl(var(--text-secondary))] group-hover:text-[hsl(var(--text-primary))] transition-colors">{res.title}</span>
                              <ChevronRight className="ml-auto h-3.5 w-3.5 text-[hsl(var(--text-muted))] group-hover:text-indigo-400 transition-colors" />
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            </div>
          )}

          {/* ─────── CAREER MATCHING ─────── */}
          {activeTab === 'career' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Career & Job Matching</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">AI-powered skill gap analysis and job recommendations</p>
              </div>

              {/* Your skills */}
              {profile?.skills && (
                <Card title="Your Skill Passport">
                  <div className="flex flex-wrap gap-2 mt-2">
                    {profile.skills.map(skill => (
                      <span key={skill} className="px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-500/15 text-indigo-400 border border-indigo-500/25">{skill}</span>
                    ))}
                  </div>
                </Card>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">Available Opportunities</p>
                  {jobs.length === 0 ? (
                    <EmptyState icon={<Briefcase className="w-8 h-8" />} title="No jobs available" description="Check back soon for new opportunities." />
                  ) : jobs.map(job => (
                    <div
                      key={job.id}
                      onClick={() => handleMatchJob(job)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all hover:border-indigo-500/40 ${selectedJob?.id === job.id ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-white/5 hover:bg-white/2'}`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <p className="font-bold text-sm text-[hsl(var(--text-primary))] truncate">{job.title}</p>
                          <p className="text-xs text-[hsl(var(--text-muted))] mt-0.5">{job.company} · {job.location}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {job.required_skills.slice(0, 4).map(skill => (
                              <span key={skill} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[hsl(var(--text-muted))]">{skill}</span>
                            ))}
                          </div>
                        </div>
                        <Button size="xs" variant="outline" loading={selectedJob?.id === job.id && jobMatchLoading}>
                          Match
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Job match result */}
                {jobMatch && selectedJob && (
                  <Card title={`Match: ${selectedJob.title}`} glow>
                    <div className="mt-3 space-y-4">
                      <div className="text-center py-2">
                        <p className="text-5xl font-extrabold gradient-text">{jobMatch.match_score}%</p>
                        <p className="text-xs text-[hsl(var(--text-muted))] mt-1">Skill Match Score</p>
                      </div>
                      <ProgressBar value={jobMatch.match_score} label="Overall Match" />

                      {jobMatch.matching_skills.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-emerald-400 mb-2 flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5" /> You Have</p>
                          <div className="flex flex-wrap gap-1.5">
                            {jobMatch.matching_skills.map(s => (
                              <span key={s} className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {jobMatch.missing_skills.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-rose-400 mb-2 flex items-center gap-1.5"><XCircle className="w-3.5 h-3.5" /> To Upskill</p>
                          <div className="flex flex-wrap gap-1.5">
                            {jobMatch.missing_skills.map(s => (
                              <span key={s} className="text-xs px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/25">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {jobMatch.recommendations.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-[hsl(var(--text-muted))] mb-2">AI Recommendations</p>
                          <ul className="space-y-1.5">
                            {jobMatch.recommendations.map((r, i) => (
                              <li key={i} className="text-xs text-[hsl(var(--text-secondary))] flex items-start gap-2">
                                <Zap className="w-3 h-3 text-indigo-400 flex-shrink-0 mt-0.5" />{r}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </Card>
                )}
              </div>
            </div>
          )}

          {/* ─────── PROJECT LAB ─────── */}
          {activeTab === 'project_lab' && (
            <div className="space-y-6 max-w-2xl animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">AI Project Lab</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Generate full project specs, architecture, and milestones with AI</p>
              </div>
              <Card title="Project Idea Generator">
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-1.5">Project Idea</label>
                    <input
                      type="text"
                      value={projectIdea}
                      onChange={e => setProjectIdea(e.target.value)}
                      className="dark-input"
                      placeholder="e.g. AI Traffic Management System"
                    />
                  </div>
                  <Button variant="primary" onClick={handleGenerateProject} loading={projectLoading} disabled={projectLoading} className="w-full glow-primary">
                    <Zap className="h-4 w-4" /> Generate SRS + Architecture + Milestones
                  </Button>

                  {projectOutput && (
                    <div className="mt-4 space-y-4 animate-fade-in-up">
                      <div className="p-4 rounded-xl border border-white/5 bg-white/2">
                        <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide mb-2">Problem Statement</p>
                        <p className="text-sm text-[hsl(var(--text-primary))] leading-relaxed">{projectOutput.problem_statement}</p>
                      </div>
                      <div className="p-4 rounded-xl border border-white/5 bg-white/2">
                        <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide mb-2">Architecture</p>
                        <p className="text-sm text-[hsl(var(--text-primary))] leading-relaxed">{projectOutput.architecture_overview}</p>
                      </div>
                      <div className="p-4 rounded-xl border border-white/5 bg-white/2">
                        <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide mb-3">Tech Stack</p>
                        <div className="flex flex-wrap gap-2">
                          {projectOutput.suggested_tech_stack?.map((t: string, i: number) => (
                            <span key={i} className="px-2.5 py-1 rounded-lg text-xs bg-indigo-500/15 text-indigo-400 border border-indigo-500/20 font-mono">{t}</span>
                          ))}
                        </div>
                      </div>
                      <div className="p-4 rounded-xl border border-white/5 bg-white/2">
                        <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide mb-3">Development Milestones</p>
                        <div className="space-y-2">
                          {projectOutput.milestones?.map((m: Record<string, unknown>, i: number) => (
                            <div key={i} className="flex items-start gap-3 text-xs">
                              <span className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-[10px] flex-shrink-0">{i + 1}</span>
                              <span className="text-[hsl(var(--text-secondary))]">{Object.values(m).join(': ')}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}

        </main>
      </div>
    </div>
  );
};
