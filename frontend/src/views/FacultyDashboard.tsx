import React, { useState } from 'react';
import { Card, Button, Badge, StatCard } from '../components/UIComponents';
import { ShieldCheck, CheckCircle, XCircle, LogOut, FileText, Bell } from 'lucide-react';

interface FacultyDashboardProps {
  userEmail: string;
  onLogout: () => void;
}

export const FacultyDashboard: React.FC<FacultyDashboardProps> = ({ userEmail, onLogout }) => {
  const [permissions, setPermissions] = useState([
    { id: 101, studentName: 'Charlie Student', rollNumber: 'STU2025001', reason: 'Fever Medical Leave', dates: '2025-08-26 to 2025-08-28', status: 'PENDING' },
    { id: 102, studentName: 'Alice Smith', rollNumber: 'STU2025042', reason: 'Hackathon Participation', dates: '2025-09-01 to 2025-09-03', status: 'PENDING' }
  ]);

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
            <h1 className="text-base font-bold">Faculty Leave & Permission Portal</h1>
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <StatCard label="Pending Leave Approvals" value={`${permissions.filter(p => p.status === 'PENDING').length} Requests`} change="Roll numbers automatically linked" icon={<FileText className="h-6 w-6" />} />
          <StatCard label="Roll Number Alerts" value="Active Sync" change="Directly mapped for attendance updates" icon={<Bell className="h-6 w-6" />} />
        </div>

        {/* Leave Permissions Approval Center */}
        <Card title="Student Leave & Permission Requests" subtitle="When a student applies for permission, their Roll Number is sent directly to faculty for easy attendance reconciliation.">
          <div className="divide-y divide-slate-200">
            {permissions.map(p => (
              <div key={p.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <p className="font-bold text-base text-slate-900">{p.studentName}</p>
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-900 font-mono font-bold text-xs rounded-lg border border-indigo-200">
                      Roll No: {p.rollNumber}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1"><span className="font-medium text-slate-800">Reason:</span> {p.reason}</p>
                  <p className="text-xs text-slate-400 mt-0.5"><span className="font-medium">Dates:</span> {p.dates}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {p.status === 'PENDING' ? (
                    <>
                      <Button variant="primary" size="sm" onClick={() => handleApproveLeave(p.id)}>
                        <CheckCircle className="h-4 w-4 mr-1" /> Approve Request
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleRejectLeave(p.id)}>
                        <XCircle className="h-4 w-4 mr-1" /> Reject Request
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
