import React, { useEffect, useState } from 'react';
import { Card, Button, Badge, StatCard } from '../components/UIComponents';
import { getPendingPermissions, updatePermission, type PermissionRequest } from '../api';
import { ShieldCheck, CheckCircle, XCircle, LogOut, FileText, Bell } from 'lucide-react';

interface FacultyDashboardProps {
  userEmail: string;
  token: string;
  onLogout: () => void;
}

export const FacultyDashboard: React.FC<FacultyDashboardProps> = ({ userEmail, token, onLogout }) => {
  const [permissions, setPermissions] = useState<PermissionRequest[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPendingPermissions(token)
      .then(setPermissions)
      .catch(requestError => setError(requestError instanceof Error ? requestError.message : 'Unable to load permissions'));
  }, [token]);

  const handlePermissionAction = async (id: number, action: 'APPROVE' | 'REJECT') => {
    try {
      const updated = await updatePermission(token, id, action);
      setPermissions(prev => prev.map(permission => permission.id === id ? updated : permission));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Permission action failed');
    }
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
        {error && <div role="alert" className="p-3 bg-rose-50 text-rose-800 border border-rose-200 rounded-lg text-sm">{error}</div>}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <StatCard label="Pending Leave Approvals" value={`${permissions.filter(p => p.status === 'PENDING').length} Requests`} change="Roll numbers automatically linked" icon={<FileText className="h-6 w-6" />} />
          <StatCard label="Roll Number Alerts" value="Active Sync" change="Directly mapped for attendance updates" icon={<Bell className="h-6 w-6" />} />
        </div>

        {/* Leave Permissions Approval Center */}
        <Card title="Student Leave & Permission Requests" subtitle="When a student applies for permission, their Roll Number is sent directly to faculty for easy attendance reconciliation.">
          <div className="divide-y divide-slate-200">
            {permissions.length === 0 && <p className="py-6 text-sm text-slate-500">No permission requests currently require review.</p>}
            {permissions.map(p => (
              <div key={p.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <p className="font-bold text-base text-slate-900">{p.student_name}</p>
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-900 font-mono font-bold text-xs rounded-lg border border-indigo-200">
                      Roll No: {p.student_roll_number}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1"><span className="font-medium text-slate-800">Reason:</span> {p.reason}</p>
                  <p className="text-xs text-slate-400 mt-0.5"><span className="font-medium">Dates:</span> {new Date(p.start_date).toLocaleDateString()} to {new Date(p.end_date).toLocaleDateString()}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {p.status === 'PENDING' || p.status === 'FACULTY_REVIEW' ? (
                    <>
                      <Button variant="primary" size="sm" onClick={() => handlePermissionAction(p.id, 'APPROVE')}>
                        <CheckCircle className="h-4 w-4 mr-1" /> Approve Request
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handlePermissionAction(p.id, 'REJECT')}>
                        <XCircle className="h-4 w-4 mr-1" /> Reject Request
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
      </main>
    </div>
  );
};
