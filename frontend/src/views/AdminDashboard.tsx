import React, { useEffect, useState } from 'react';
import { Card, StatCard, Badge, Button } from '../components/UIComponents';
import { getAdminOverview, type AdminOverview } from '../api';
import { Building2, Users, FileText, Activity, ShieldAlert, LogOut } from 'lucide-react';

interface AdminDashboardProps {
  userEmail: string;
  token: string;
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ userEmail, token, onLogout }) => {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAdminOverview(token)
      .then(setOverview)
      .catch(requestError => setError(requestError instanceof Error ? requestError.message : 'Unable to load analytics'));
  }, [token]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-slate-900 text-white border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-rose-600 rounded-xl">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-base font-bold">University Administration Console</h1>
            <p className="text-xs text-slate-400">{userEmail} • Super Administrator</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="danger">System Admin</Badge>
          <Button variant="ghost" size="sm" onClick={onLogout} className="text-slate-300 hover:text-white">
            <LogOut className="h-4 w-4 mr-1" /> Logout
          </Button>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        {error && <div role="alert" className="p-3 bg-rose-50 text-rose-800 border border-rose-200 rounded-lg text-sm">{error}</div>}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard label="Enrolled Students" value={overview?.total_students ?? '...'} change="Live database count" icon={<Users className="h-6 w-6" />} />
          <StatCard label="Average Attendance" value={overview ? `${overview.attendance_percentage}%` : '...'} change="Recorded attendance" icon={<Activity className="h-6 w-6" />} />
          <StatCard label="Approved Services" value={overview?.approved_services ?? '...'} change="Processed requests" icon={<FileText className="h-6 w-6" />} />
          <StatCard label="Audit Events" value={overview?.audit_events ?? '...'} change="Immutable records" icon={<ShieldAlert className="h-6 w-6" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="System Audit Logs">
            <div className="space-y-3 font-mono text-xs text-slate-700">
              {overview?.recent_audit_logs.length ? overview.recent_audit_logs.map((log, index) => (
                <div key={`${log.action}-${index}`} className="p-2.5 bg-slate-100 rounded border">
                  {new Date(log.timestamp).toLocaleString()} | ACTOR: {log.actor_id ?? 'SYSTEM'} | ACTION: {log.action} | RESOURCE: {log.resource}
                </div>
              )) : <p className="text-sm text-slate-500">No audit events recorded yet.</p>}
            </div>
          </Card>

          <Card title="University RAG Knowledge Base Management">
            <div className="space-y-3">
              <div className="p-3 border rounded-lg flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm">University Attendance Regulations</p>
                  <p className="text-xs text-slate-500">Category: REGULATIONS • 4 Chunks</p>
                </div>
                <Badge variant="success">Active RAG</Badge>
              </div>
              <div className="p-3 border rounded-lg flex items-center justify-between">
                <div>
                  <p className="font-semibold text-sm">Digital ID & Service Procedures</p>
                  <p className="text-xs text-slate-500">Category: SERVICES • 2 Chunks</p>
                </div>
                <Badge variant="success">Active RAG</Badge>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};
