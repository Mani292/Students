import React, { useEffect, useState } from 'react';
import { Card, Button, Badge, StatCard } from '../components/UIComponents';
import { applyPermission, createService, getDigitalId, getMyPermissions, getMyServices, sendAIMessage, type PermissionRequest, type ServiceRequest } from '../api';
import {
  LayoutDashboard, FileText, Award, Bot, BookOpen, Briefcase, Code, User, LogOut, Send
} from 'lucide-react';

interface StudentPortalProps {
  userEmail: string;
  token: string;
  onLogout: () => void;
}

export const StudentPortal: React.FC<StudentPortalProps> = ({ userEmail, token, onLogout }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'permissions' | 'services' | 'digital_id' | 'copilot' | 'learning' | 'career' | 'project_lab'>('overview');

  // Interactive AI Assistant State
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string; tools?: string[] }>>([
    { sender: 'ai', text: 'Hello! I am your Smart University AI Assistant. How can I assist you with your academics, attendance, or career today?' }
  ]);
  const [chatInput, setChatInput] = useState('');

  const [requestError, setRequestError] = useState<string | null>(null);

  // Leave Form State
  const [leaveReason, setLeaveReason] = useState('');
  const [leaveSubmitted, setLeaveSubmitted] = useState(false);

  // Service Request State
  const [serviceType, setServiceType] = useState('BONAFIDE');
  const [serviceSubmitted, setServiceSubmitted] = useState(false);
  const [permissions, setPermissions] = useState<PermissionRequest[]>([]);
  const [services, setServices] = useState<ServiceRequest[]>([]);
  const [digitalId, setDigitalId] = useState<Record<string, string | number> | null>(null);

  // Project Lab State
  const [projectIdea, setProjectIdea] = useState('AI Traffic Management');
  const [projectOutput, setProjectOutput] = useState<any>(null);

  useEffect(() => {
    Promise.all([getMyPermissions(token), getMyServices(token), getDigitalId(token)])
      .then(([permissionData, serviceData, idData]) => {
        setPermissions(permissionData);
        setServices(serviceData);
        setDigitalId(idData);
      })
      .catch(error => setRequestError(error instanceof Error ? error.message : 'Unable to load student data'));
  }, [token]);

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setChatInput('');
    try {
      const result = await sendAIMessage(token, userMsg);
      setMessages(prev => [...prev, { sender: 'ai', text: result.response, tools: result.tools_used }]);
    } catch (error) {
      setMessages(prev => [...prev, { sender: 'ai', text: error instanceof Error ? error.message : 'AI request failed' }]);
    }
  };

  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const permission = await applyPermission(token, leaveReason);
      setPermissions(prev => [permission, ...prev]);
      setLeaveReason('');
      setLeaveSubmitted(true);
    } catch (error) {
      setRequestError(error instanceof Error ? error.message : 'Permission request failed');
    }
  };

  const handleCreateService = async () => {
    try {
      const service = await createService(token, serviceType);
      setServices(prev => [service, ...prev]);
      setServiceSubmitted(true);
    } catch (error) {
      setRequestError(error instanceof Error ? error.message : 'Service request failed');
    }
  };

  const handleGenerateProject = () => {
    setProjectOutput({
      problem: `Automating and optimizing real-time data handling for ${projectIdea}.`,
      architecture: "Decoupled React Frontend + FastAPI Backend + PostgreSQL DB",
      milestones: [
        "Week 1: Requirements Gathering & Schema Design",
        "Week 2: Core Microservice Development",
        "Week 3: AI Integration & Testing",
        "Week 4: Final Documentation & Presentation"
      ]
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Topbar */}
      <header className="bg-slate-900 text-white border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-sky-600 rounded-xl">
            <User className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-base font-bold">Smart Student Portal</h1>
            <p className="text-xs text-slate-400">{userEmail} • Authenticated student</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="success">Active Session</Badge>
          <Button variant="ghost" size="sm" onClick={onLogout} className="text-slate-300 hover:text-white">
            <LogOut className="h-4 w-4 mr-1" /> Logout
          </Button>
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-slate-200 p-4 space-y-1 hidden md:block">
          {[
            { id: 'overview', label: 'Overview', icon: LayoutDashboard },
            { id: 'permissions', label: 'Permissions & Leave', icon: FileText },
            { id: 'services', label: 'Service Center', icon: Award },
            { id: 'digital_id', label: 'Digital Student ID', icon: User },
            { id: 'copilot', label: 'AI Copilot Chat', icon: Bot },
            { id: 'learning', label: 'AI Learning Hub', icon: BookOpen },
            { id: 'career', label: 'Career & Matching', icon: Briefcase },
            { id: 'project_lab', label: 'AI Project Lab', icon: Code },
          ].map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === item.id ? 'bg-sky-50 text-sky-700 font-semibold' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </aside>

        {/* Content View */}
        <main className="flex-1 p-6 overflow-y-auto">
          {requestError && (
            <div role="alert" className="mb-6 p-3 bg-rose-50 text-rose-800 border border-rose-200 rounded-lg text-sm">
              {requestError}
            </div>
          )}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard label="Current CGPA" value="3.84" change="Top 5% in Department" icon={<Award className="h-6 w-6" />} />
                <StatCard label="Pending Requests" value={`${permissions.filter(request => request.status !== 'APPROVED' && request.status !== 'REJECTED').length} Leave`} change="Live from API" icon={<FileText className="h-6 w-6" />} />
                <StatCard label="Active AI Roadmap" value="Python ML" change="Step 3 of 4" icon={<BookOpen className="h-6 w-6" />} />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Upcoming Classes Today">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">CS101 - Database Management Systems</p>
                        <p className="text-xs text-slate-500">Room 301 • 10:00 AM - 11:30 AM</p>
                      </div>
                      <Badge variant="info">Active Now</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">CS204 - Operating Systems</p>
                        <p className="text-xs text-slate-500">Room 204 • 02:00 PM - 03:30 PM</p>
                      </div>
                      <Badge variant="neutral">Upcoming</Badge>
                    </div>
                  </div>
                </Card>

                <Card title="AI Recommendations & Career Insights">
                  <div className="space-y-3 text-sm">
                    <div className="p-3 bg-sky-50 text-sky-900 rounded-lg border border-sky-200">
                      <p className="font-semibold">💡 Learning Opportunity</p>
                      <p className="text-xs mt-1">Based on your skills (Python, FastAPI), completing the 'Docker Basics' module will boost your ATS match score by 18%.</p>
                    </div>
                    <div className="p-3 bg-emerald-50 text-emerald-900 rounded-lg border border-emerald-200">
                      <p className="font-semibold">🎯 Job Recommendation</p>
                      <p className="text-xs mt-1">Full-Stack Intern at TechCorp matching 85% of your achievement profile.</p>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'permissions' && (
            <div className="space-y-6 max-w-2xl">
              <Card title="Apply for Leave / Permission">
                {leaveSubmitted && (
                  <div className="mb-4 p-3 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg text-sm">
                    Leave Request Submitted! Workflow status set to: PENDING (FACULTY_REVIEW)
                  </div>
                )}
                <form onSubmit={handleApplyLeave} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Reason for Leave</label>
                    <textarea
                      required
                      rows={3}
                      value={leaveReason}
                      onChange={(e) => setLeaveReason(e.target.value)}
                      placeholder="Specify medical or personal details..."
                      className="mt-1 block w-full p-3 border border-slate-300 rounded-lg text-sm"
                    />
                  </div>
                  <Button type="submit" variant="primary" className="w-full">
                    Submit Request
                  </Button>
                </form>
                <div className="mt-6 space-y-2">
                  {permissions.length === 0 && <p className="text-sm text-slate-500">No permission requests yet.</p>}
                  {permissions.map(permission => (
                    <div key={permission.id} className="p-3 border border-slate-200 rounded-lg flex items-center justify-between text-sm">
                      <span>{permission.reason}</span>
                      <Badge variant={permission.status === 'APPROVED' ? 'success' : 'warning'}>{permission.status}</Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'services' && (
            <div className="space-y-6 max-w-2xl">
              <Card title="Digital University Service Request Center">
                {serviceSubmitted && (
                  <div className="mb-4 p-3 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg text-sm">
                    Service request created! Reference #SRV-9082. Status: SUBMITTED
                  </div>
                )}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Select Certificate / Request Type</label>
                    <select
                      value={serviceType}
                      onChange={(e) => setServiceType(e.target.value)}
                      className="mt-1 block w-full p-2.5 border border-slate-300 rounded-lg text-sm"
                    >
                      <option value="BONAFIDE">Bonafide Certificate</option>
                      <option value="ID_CARD">Replacement ID Card</option>
                      <option value="HOSTEL">Hostel Allocation Request</option>
                      <option value="TRANSPORT">Transport Bus Pass</option>
                    </select>
                  </div>
                  <Button variant="primary" className="w-full" onClick={handleCreateService}>
                    Issue Request
                  </Button>
                </div>
                <div className="mt-6 space-y-2">
                  {services.length === 0 && <p className="text-sm text-slate-500">No service requests yet.</p>}
                  {services.map(service => (
                    <div key={service.id} className="p-3 border border-slate-200 rounded-lg flex items-center justify-between text-sm">
                      <span>{service.service_type}</span>
                      <Badge variant="info">{service.status}</Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'digital_id' && (
            <div className="space-y-6 max-w-md mx-auto">
              <Card className="bg-gradient-to-br from-slate-900 to-sky-950 text-white border-none p-6 rounded-2xl shadow-xl">
                <div className="flex items-center justify-between pb-4 border-b border-slate-700">
                  <span className="text-xs font-bold uppercase tracking-wider text-sky-400">Smart University Digital ID</span>
                  <Badge variant="success">Verified</Badge>
                </div>
                <div className="mt-6 flex items-center space-x-4">
                  <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center text-2xl font-bold text-white border-2 border-sky-400">
                    {String(digitalId?.full_name ?? userEmail).slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">{digitalId?.full_name ?? 'Loading student ID...'}</h3>
                    <p className="text-xs text-slate-300">Roll: {digitalId?.roll_number ?? '...'}</p>
                    <p className="text-xs text-slate-400">Dept: {digitalId?.department_name ?? '...'}</p>
                  </div>
                </div>
                <div className="mt-6 bg-white p-4 rounded-xl text-slate-900 flex flex-col items-center justify-center">
                  <div className="w-32 h-32 bg-slate-100 border border-slate-300 flex items-center justify-center text-xs font-mono text-center p-2 rounded-lg">
                    {digitalId?.verification_token ? 'Signed verification token available' : 'Loading signed token...'}
                  </div>
                  <p className="text-[10px] text-slate-500 mt-2 font-mono break-all">{digitalId?.verification_token ?? 'Token unavailable'}</p>
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'copilot' && (
            <div className="h-[600px] flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 bg-slate-900 text-white font-bold flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Bot className="h-5 w-5 text-sky-400" />
                  <span>University AI Copilot Assistant</span>
                </div>
                <Badge variant="info">GLM-4.7 & RAG Active</Badge>
              </div>
              <div className="flex-1 p-4 overflow-y-auto space-y-4">
                {messages.map((m, idx) => (
                  <div key={idx} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-md p-3.5 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-sky-600 text-white' : 'bg-slate-100 text-slate-800'}`}>
                      <p>{m.text}</p>
                      {m.tools && (
                        <div className="mt-2 pt-2 border-t border-slate-200/50 text-[10px] text-slate-500 font-mono">
                          🔧 Executed Tools: {m.tools.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 border-t border-slate-200 flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Ask about attendance, policies, or career..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 p-2.5 border border-slate-300 rounded-lg text-sm"
                />
                <Button variant="primary" onClick={handleSendMessage}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'learning' && (
            <div className="space-y-6">
              <Card title="AI Personalized Learning Roadmap">
                <p className="text-sm text-slate-600 mb-4">Target: Python & Machine Learning Engineer</p>
                <div className="space-y-3">
                  {[
                    { step: 1, title: 'Programming Fundamentals', status: 'Completed' },
                    { step: 2, title: 'Object-Oriented Programming & Data Structures', status: 'Completed' },
                    { step: 3, title: 'NumPy, Pandas & Data Analysis', status: 'In Progress' },
                    { step: 4, title: 'Machine Learning Models & Deployment', status: 'Upcoming' },
                  ].map(s => (
                    <div key={s.step} className="p-3 border rounded-lg flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-sm">Step {s.step}: {s.title}</p>
                      </div>
                      <Badge variant={s.status === 'Completed' ? 'success' : s.status === 'In Progress' ? 'info' : 'neutral'}>
                        {s.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'career' && (
            <div className="space-y-6">
              <Card title="AI Job Matching & Resume Optimizer">
                <div className="p-4 bg-sky-50 text-sky-900 rounded-lg border border-sky-200 mb-4">
                  <h4 className="font-bold text-sm">ATS Match Score: 85%</h4>
                  <p className="text-xs mt-1">Matched Skills: Python, FastAPI, SQL | Missing: Docker, AWS</p>
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'project_lab' && (
            <div className="space-y-6 max-w-2xl">
              <Card title="AI Project Lab & Workspace Mentor">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Project Idea / Title</label>
                    <input
                      type="text"
                      value={projectIdea}
                      onChange={(e) => setProjectIdea(e.target.value)}
                      className="mt-1 block w-full p-2.5 border border-slate-300 rounded-lg text-sm"
                    />
                  </div>
                  <Button variant="primary" onClick={handleGenerateProject}>
                    Generate SRS, DB Schema & Development Milestones
                  </Button>

                  {projectOutput && (
                    <div className="mt-4 p-4 bg-slate-50 border rounded-lg space-y-3 text-sm">
                      <p><strong>Problem Statement:</strong> {projectOutput.problem}</p>
                      <p><strong>Architecture:</strong> {projectOutput.architecture}</p>
                      <div>
                        <strong>Milestones:</strong>
                        <ul className="list-disc pl-5 text-xs text-slate-600 mt-1">
                          {projectOutput.milestones.map((m: string, i: number) => <li key={i}>{m}</li>)}
                        </ul>
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
