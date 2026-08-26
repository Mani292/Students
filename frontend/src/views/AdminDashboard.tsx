import React from 'react';
import { Card, StatCard, Badge, Button } from '../components/UIComponents';
import { Building2, Users, FileText, Activity, ShieldAlert, LogOut } from 'lucide-react';

interface AdminDashboardProps {
  userEmail: string;
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ userEmail, onLogout }) => {
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard label="Total Enrolled Students" value="2,450" change="+120 this semester" icon={<Users className="h-6 w-6" />} />
          <StatCard label="Avg Ecosystem Attendance" value="84.2%" change="Optimal range" icon={<Activity className="h-6 w-6" />} />
          <StatCard label="Service Requests Issued" value="482" change="98% approval rate" icon={<FileText className="h-6 w-6" />} />
          <StatCard label="Security & Audit Events" value="1,240" change="All logged" icon={<ShieldAlert className="h-6 w-6" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="System Audit Logs">
            <div className="space-y-3 font-mono text-xs text-slate-700">
              <div className="p-2.5 bg-slate-100 rounded border">
                [2025-08-25 10:14:02] ACTOR: fac_001 | ACTION: ATTENDANCE_SESSION_STARTED | RESOURCE: class_cs101
              </div>
              <div className="p-2.5 bg-slate-100 rounded border">
                [2025-08-25 10:15:22] ACTOR: stud_002 | ACTION: ATTENDANCE_RECORDED | STATUS: FLAGGED (DUPLICATE_DEVICE)
              </div>
              <div className="p-2.5 bg-slate-100 rounded border">
                [2025-08-25 10:18:45] ACTOR: hod_mech | ACTION: PERMISSION_APPROVED | RESOURCE: request_101
              </div>
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
