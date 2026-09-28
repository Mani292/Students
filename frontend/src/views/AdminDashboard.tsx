import React, { useEffect, useState } from 'react';
import { Card, StatCard, Badge, Button, Avatar, EmptyState, Alert, LoadingSpinner, ProgressBar } from '../components/UIComponents';
import { getAdminOverview, type AdminOverview } from '../api';
import {
  Building2, Users, FileText, Activity, ShieldAlert, LogOut,
  GraduationCap, BarChart2, BookOpen, Settings,
  RefreshCw, Download, Eye, EyeOff,
} from 'lucide-react';

interface AdminDashboardProps {
  userEmail: string;
  token: string;
  onLogout: () => void;
}

type AdminTab = 'analytics' | 'users' | 'knowledge' | 'audit' | 'settings';

// ── Mini bar chart using CSS ──
const MiniBarChart: React.FC<{ data: { label: string; value: number; max: number }[]; title: string }> = ({ data, title }) => (
  <div>
    <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide mb-3">{title}</p>
    <div className="space-y-2.5">
      {data.map((d, i) => (
        <div key={i} className="flex items-center gap-3">
          <span className="text-[11px] text-[hsl(var(--text-muted))] w-8 text-right flex-shrink-0">{d.label}</span>
          <div className="flex-1 h-5 rounded-lg overflow-hidden" style={{ background: 'hsl(var(--surface-4))' }}>
            <div
              className="h-full rounded-lg flex items-center justify-end pr-2 transition-all duration-700"
              style={{
                width: `${Math.round((d.value / d.max) * 100)}%`,
                background: 'linear-gradient(90deg, hsl(217,91%,60%), hsl(262,83%,58%))',
                minWidth: 24,
              }}
            >
              <span className="text-[10px] text-white font-bold">{d.value}%</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ── Mock user data ──
const mockUsers = [
  { id: 1, name: 'Arjun Kumar', email: 'student@univ.edu', role: 'STUDENT', active: true, dept: 'CSE' },
  { id: 2, name: 'Dr. Priya Sharma', email: 'faculty@univ.edu', role: 'FACULTY', active: true, dept: 'CSE' },
  { id: 3, name: 'Admin User', email: 'admin@univ.edu', role: 'ADMIN', active: true, dept: 'ADMIN' },
  { id: 4, name: 'Riya Patel', email: 'riya@univ.edu', role: 'STUDENT', active: true, dept: 'ECE' },
  { id: 5, name: 'Vikram Singh', email: 'vikram@univ.edu', role: 'STUDENT', active: false, dept: 'MECH' },
  { id: 6, name: 'Dr. Anjali Mehta', email: 'anjali@univ.edu', role: 'FACULTY', active: true, dept: 'MBA' },
  { id: 7, name: 'Prof. Suresh Nair', email: 'suresh@univ.edu', role: 'HOD', active: true, dept: 'CSE' },
];

const mockKnowledgeDocs = [
  { title: 'Attendance Regulations 2024', category: 'REGULATIONS', chunks: 4, active: true, updated: '2024-08-01' },
  { title: 'Digital ID & Service Procedures', category: 'SERVICES', chunks: 2, active: true, updated: '2024-07-15' },
  { title: 'Academic Calendar & Holiday List', category: 'ACADEMIC', chunks: 6, active: true, updated: '2024-06-01' },
  { title: 'Library Rules & Borrowing Policy', category: 'LIBRARY', chunks: 3, active: false, updated: '2024-05-20' },
  { title: 'Hostel Allocation Guidelines', category: 'HOSTEL', chunks: 5, active: true, updated: '2024-07-01' },
];

const attendanceTrend = [
  { label: 'Mon', value: 91, max: 100 },
  { label: 'Tue', value: 87, max: 100 },
  { label: 'Wed', value: 94, max: 100 },
  { label: 'Thu', value: 88, max: 100 },
  { label: 'Fri', value: 76, max: 100 },
];

const deptBreakdown = [
  { label: 'CSE', value: 92, max: 100 },
  { label: 'ECE', value: 85, max: 100 },
  { label: 'MECH', value: 78, max: 100 },
  { label: 'MBA', value: 88, max: 100 },
  { label: 'CIVIL', value: 82, max: 100 },
];

const roleColors: Record<string, 'success' | 'info' | 'purple' | 'warning'> = {
  STUDENT: 'info', FACULTY: 'success', ADMIN: 'danger' as any, HOD: 'purple', SUPER_ADMIN: 'danger' as any,
};

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ userEmail, token, onLogout }) => {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<AdminTab>('analytics');
  const [users, setUsers] = useState(mockUsers);
  const [userSearch, setUserSearch] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchOverview = () => {
    setRefreshing(true);
    getAdminOverview(token)
      .then(setOverview)
      .catch(err => setError(err instanceof Error ? err.message : 'Could not load analytics'))
      .finally(() => { setLoading(false); setRefreshing(false); });
  };

  useEffect(() => { fetchOverview(); }, [token]);

  const toggleUser = (id: number) => {
    setUsers(prev => prev.map(u => u.id === id ? { ...u, active: !u.active } : u));
  };

  const filteredUsers = users.filter(u =>
    u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.role.toLowerCase().includes(userSearch.toLowerCase())
  );

  const navItems: { id: AdminTab; label: string; icon: React.ElementType }[] = [
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
    { id: 'users',     label: 'User Management', icon: Users },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'audit',     label: 'Audit Logs', icon: ShieldAlert },
    { id: 'settings',  label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'hsl(var(--surface-1))' }}>

      {/* ===== TOPBAR ===== */}
      <header className="border-b px-5 py-3 flex items-center justify-between sticky top-0 z-40 glass"
              style={{ borderColor: 'hsl(var(--surface-border))' }}>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-rose-500 to-pink-600 shadow-lg">
            <Building2 className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-[hsl(var(--text-primary))]">Administration Console</h1>
            <p className="text-[10px] text-[hsl(var(--text-muted))]">SmartUniv · Super Admin</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="danger">System Admin</Badge>
          <Button variant="ghost" size="sm" onClick={fetchOverview} disabled={refreshing}>
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
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
                <span className="flex-1 text-left text-sm">{item.label}</span>
              </button>
            );
          })}
        </aside>

        {/* ===== CONTENT ===== */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && <Alert type="danger" onClose={() => setError(null)}>{error}</Alert>}

          {/* ─── ANALYTICS TAB ─── */}
          {activeTab === 'analytics' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Platform Analytics</h2>
                <p className="text-sm text-[hsl(var(--text-muted))]">Live metrics from the university database</p>
              </div>

              {/* KPI cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Total Students" value={loading ? '...' : (overview?.total_students ?? 0)} change="Enrolled" iconColor="from-blue-500 to-indigo-600" icon={<GraduationCap className="h-5 w-5" />} changeType="positive" />
                <StatCard label="Avg Attendance" value={loading ? '...' : `${overview?.attendance_percentage ?? 0}%`} change="Platform-wide" iconColor="from-emerald-500 to-teal-600" icon={<Activity className="h-5 w-5" />} changeType="positive" />
                <StatCard label="Approved Services" value={loading ? '...' : (overview?.approved_services ?? 0)} change="Processed" iconColor="from-amber-500 to-orange-500" icon={<FileText className="h-5 w-5" />} changeType="positive" />
                <StatCard label="Audit Events" value={loading ? '...' : (overview?.audit_events ?? 0)} change="Immutable log" iconColor="from-rose-500 to-pink-600" icon={<ShieldAlert className="h-5 w-5" />} changeType="neutral" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Attendance trend chart */}
                <Card title="Attendance Trend — This Week">
                  <div className="mt-4">
                    <MiniBarChart data={attendanceTrend} title="Daily Rate" />
                  </div>
                </Card>

                {/* Dept breakdown */}
                <Card title="Attendance by Department">
                  <div className="mt-4">
                    <MiniBarChart data={deptBreakdown} title="Department Rate" />
                  </div>
                </Card>

                {/* Service requests breakdown */}
                <Card title="Service Requests" subtitle="By type this month">
                  <div className="space-y-3 mt-4">
                    {[
                      { label: 'Bonafide Certificate', count: 34, color: 'from-blue-500 to-indigo-600' },
                      { label: 'ID Card Replacement', count: 12, color: 'from-amber-500 to-orange-500' },
                      { label: 'Transport Bus Pass', count: 21, color: 'from-emerald-500 to-teal-600' },
                      { label: 'Hostel Allocation', count: 8, color: 'from-purple-500 to-indigo-600' },
                    ].map((s, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${s.color} flex-shrink-0`} />
                        <span className="text-xs text-[hsl(var(--text-secondary))] flex-1">{s.label}</span>
                        <span className="text-xs font-bold text-[hsl(var(--text-primary))]">{s.count}</span>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* System health */}
                <Card title="System Health">
                  <div className="space-y-4 mt-4">
                    <ProgressBar value={98} label="API Response Rate" />
                    <ProgressBar value={76} label="DB Utilisation" color="linear-gradient(135deg, #f59e0b, #d97706)" />
                    <ProgressBar value={45} label="Storage Used" color="linear-gradient(135deg, #10b981, #059669)" />
                    <ProgressBar value={overview ? Math.min(100, overview.attendance_percentage) : 88} label="Avg Attendance" />
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* ─── USERS TAB ─── */}
          {activeTab === 'users' && (
            <div className="space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">User Management</h2>
                  <p className="text-sm text-[hsl(var(--text-muted))]">{users.filter(u => u.active).length} active · {users.filter(u => !u.active).length} deactivated</p>
                </div>
                <Button variant="primary" size="sm">
                  <Users className="h-4 w-4" /> Add User
                </Button>
              </div>

              <input
                type="text"
                placeholder="Search by name, email, or role..."
                value={userSearch}
                onChange={e => setUserSearch(e.target.value)}
                className="dark-input w-full max-w-sm"
              />

              <Card>
                <div className="overflow-x-auto -mx-6 px-6">
                  <table className="w-full min-w-[600px]">
                    <thead>
                      <tr className="border-b border-white/10">
                        {['User', 'Role', 'Department', 'Status', 'Actions'].map(h => (
                          <th key={h} className="text-left py-3 px-3 text-[11px] font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wide">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {filteredUsers.map(u => (
                        <tr key={u.id} className="hover:bg-white/2 transition-colors">
                          <td className="py-3.5 px-3">
                            <div className="flex items-center gap-2.5">
                              <Avatar name={u.name} size="sm" />
                              <div>
                                <p className="text-xs font-semibold text-[hsl(var(--text-primary))]">{u.name}</p>
                                <p className="text-[10px] text-[hsl(var(--text-muted))]">{u.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="py-3.5 px-3">
                            <Badge variant={(roleColors[u.role] ?? 'neutral') as any} size="sm">{u.role}</Badge>
                          </td>
                          <td className="py-3.5 px-3 text-xs text-[hsl(var(--text-secondary))]">{u.dept}</td>
                          <td className="py-3.5 px-3">
                            <Badge variant={u.active ? 'success' : 'neutral'} dot={u.active}>{u.active ? 'Active' : 'Inactive'}</Badge>
                          </td>
                          <td className="py-3.5 px-3">
                            <button
                              onClick={() => toggleUser(u.id)}
                              className="text-[11px] flex items-center gap-1.5 text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text-primary))] transition-colors"
                            >
                              {u.active ? <><EyeOff className="w-3.5 h-3.5" /> Deactivate</> : <><Eye className="w-3.5 h-3.5" /> Activate</>}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {filteredUsers.length === 0 && (
                    <EmptyState icon={<Users className="w-8 h-8" />} title="No users found" description="Try a different search term." />
                  )}
                </div>
              </Card>
            </div>
          )}

          {/* ─── KNOWLEDGE BASE TAB ─── */}
          {activeTab === 'knowledge' && (
            <div className="space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">RAG Knowledge Base</h2>
                  <p className="text-sm text-[hsl(var(--text-muted))]">Documents used by the AI Copilot for retrieval</p>
                </div>
                <Button variant="primary" size="sm"><BookOpen className="h-4 w-4" /> Upload Document</Button>
              </div>
              <div className="space-y-3">
                {mockKnowledgeDocs.map((doc, i) => (
                  <Card key={i}>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <p className="font-semibold text-sm text-[hsl(var(--text-primary))]">{doc.title}</p>
                          <Badge variant={doc.active ? 'success' : 'neutral'} size="sm">{doc.active ? 'Active' : 'Inactive'}</Badge>
                        </div>
                        <div className="flex items-center gap-3 text-[11px] text-[hsl(var(--text-muted))]">
                          <span className="px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-400 font-mono">{doc.category}</span>
                          <span>{doc.chunks} chunks</span>
                          <span>Updated {doc.updated}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <Button variant="ghost" size="xs"><Download className="h-3.5 w-3.5" /></Button>
                        <Button variant="outline" size="xs">{doc.active ? 'Deactivate' : 'Activate'}</Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* ─── AUDIT LOGS TAB ─── */}
          {activeTab === 'audit' && (
            <div className="space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">System Audit Logs</h2>
                  <p className="text-sm text-[hsl(var(--text-muted))]">Immutable record of all platform actions</p>
                </div>
                <Button variant="outline" size="sm"><Download className="h-4 w-4" /> Export CSV</Button>
              </div>
              <Card>
                {overview?.recent_audit_logs.length ? (
                  <div className="space-y-2 -mx-6 px-6">
                    {overview.recent_audit_logs.map((log, i) => (
                      <div key={i} className="flex items-start gap-3 py-3 border-b border-white/5 last:border-0">
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-mono font-bold text-[hsl(var(--text-primary))]">{log.action}</span>
                            <span className="text-[10px] text-[hsl(var(--text-muted))]">on {log.resource}</span>
                            {log.actor_id && <Badge variant="neutral" size="sm">Actor #{log.actor_id}</Badge>}
                          </div>
                          <p className="text-[10px] text-[hsl(var(--text-muted))] mt-0.5">{new Date(log.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : loading ? (
                  <div className="flex justify-center py-8"><LoadingSpinner /></div>
                ) : (
                  <EmptyState icon={<ShieldAlert className="w-8 h-8" />} title="No audit events yet" description="Events will appear here as users interact with the platform." />
                )}
              </Card>
            </div>
          )}

          {/* ─── SETTINGS TAB ─── */}
          {activeTab === 'settings' && (
            <div className="space-y-6 animate-fade-in max-w-2xl">
              <h2 className="text-xl font-bold text-[hsl(var(--text-primary))]">Platform Settings</h2>
              {[
                { label: 'University Name', value: 'SmartUniv — University of Technology', type: 'text' },
                { label: 'Contact Email', value: 'admin@smartuniv.io', type: 'email' },
                { label: 'Max Attendance Window (seconds)', value: '30', type: 'number' },
                { label: 'CORS Origins', value: 'http://localhost:5173,https://app.smartuniv.io', type: 'text' },
              ].map((s, i) => (
                <Card key={i}>
                  <label className="block text-xs font-semibold text-[hsl(var(--text-secondary))] mb-2">{s.label}</label>
                  <input type={s.type} defaultValue={s.value} className="dark-input" />
                </Card>
              ))}
              <Button variant="primary" className="glow-primary">Save Settings</Button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
