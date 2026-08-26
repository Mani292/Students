const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

export interface SessionUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  role: string;
  email: string;
}

export interface Session {
  token: string;
  refreshToken: string;
  user: SessionUser;
}

export interface PermissionRequest {
  id: number;
  student_id: number;
  student_roll_number?: string;
  student_name?: string;
  reason: string;
  start_date: string;
  end_date: string;
  proof_url?: string;
  comments?: string;
  status: string;
  created_at: string;
}

export interface ServiceRequest {
  id: number;
  student_id: number;
  service_type: string;
  details: Record<string, unknown>;
  status: string;
  issued_document_url?: string;
  created_at: string;
}

export interface AIChatResponse {
  response: string;
  sources: Array<Record<string, unknown>>;
  tools_used: string[];
}

export interface AdminOverview {
  total_students: number;
  total_faculty: number;
  attendance_percentage: number;
  approved_services: number;
  audit_events: number;
  pending_permissions: number;
  recent_audit_logs: Array<{
    action: string;
    resource: string;
    timestamp: string;
    actor_id?: number;
    details: Record<string, unknown>;
  }>;
}

export interface AcademicProfile {
  full_name: string;
  roll_number: string;
  department: string;
  year: number;
  semester: number;
  cgpa: number;
  skills: string[];
}

export interface LearningPath {
  subject: string;
  roadmap: Array<{ step: number; title: string; description: string }>;
  recommended_resources: Array<{ type: string; title: string; url: string }>;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  required_skills: string[];
}

export interface JobMatch {
  match_score: number;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
}

export interface ProjectMentorOutput {
  problem_statement: string;
  objectives: string[];
  functional_requirements: string[];
  architecture_overview: string;
  suggested_tech_stack: string[];
  milestones: Array<Record<string, unknown>>;
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  category: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<Session> {
  const session = await request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const user = await request<SessionUser>('/auth/me', {}, session.access_token);
  return { token: session.access_token, refreshToken: session.refresh_token, user };
}

export async function refreshSession(refreshToken: string): Promise<Session> {
  const session = await request<LoginResponse>('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  const user = await request<SessionUser>('/auth/me', {}, session.access_token);
  return { token: session.access_token, refreshToken: session.refresh_token, user };
}

export function getNotifications(token: string) {
  return request<Notification[]>('/notifications/me', {}, token);
}

export function markNotificationRead(token: string, id: number) {
  return request<Notification>(`/notifications/${id}/read`, { method: 'PATCH' }, token);
}

export function getMyPermissions(token: string) {
  return request<PermissionRequest[]>('/permissions/my-requests', {}, token);
}

export function getPendingPermissions(token: string) {
  return request<PermissionRequest[]>('/permissions/pending', {}, token);
}

export function updatePermission(token: string, id: number, action: 'APPROVE' | 'REJECT') {
  return request<PermissionRequest>(`/permissions/${id}/action`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  }, token);
}

export function applyPermission(token: string, reason: string) {
  const now = new Date();
  const end = new Date(now);
  end.setDate(end.getDate() + 1);
  return request<PermissionRequest>('/permissions/apply', {
    method: 'POST',
    body: JSON.stringify({ reason, start_date: now.toISOString(), end_date: end.toISOString() }),
  }, token);
}

export function getMyServices(token: string) {
  return request<ServiceRequest[]>('/services/my-requests', {}, token);
}

export function createService(token: string, serviceType: string) {
  return request<ServiceRequest>('/services/request', {
    method: 'POST',
    body: JSON.stringify({ service_type: serviceType, details: {} }),
  }, token);
}

export function getDigitalId(token: string) {
  return request<Record<string, string | number>>('/services/digital-id/me', {}, token);
}

export function sendAIMessage(token: string, message: string) {
  return request<AIChatResponse>('/ai/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }, token);
}

export function getAdminOverview(token: string) {
  return request<AdminOverview>('/admin/overview', {}, token);
}

export function getAcademicProfile(token: string) {
  return request<AcademicProfile>('/academic/me', {}, token);
}

export function generateLearningPath(token: string, subject: string, careerGoal: string) {
  return request<LearningPath>('/ai/learning-path', {
    method: 'POST',
    body: JSON.stringify({ subject, career_goal: careerGoal }),
  }, token);
}

export function getJobs() {
  return request<Job[]>('/career-project/jobs');
}

export function matchJob(jobDescription: string, studentSkills: string[]) {
  return request<JobMatch>('/career-project/match-job', {
    method: 'POST',
    body: JSON.stringify({ job_description: jobDescription, student_skills: studentSkills }),
  });
}

export function generateProjectMentor(token: string, projectIdea: string) {
  return request<ProjectMentorOutput>('/career-project/project-mentor', {
    method: 'POST',
    body: JSON.stringify({ project_idea: projectIdea }),
  }, token);
}

export function recordAttendance(token: string, sessionToken: string, totpCode: string, deviceFingerprint: string) {
  return request<{ status: string }>('/attendance/record', {
    method: 'POST',
    body: JSON.stringify({ session_token: sessionToken, totp_code: totpCode, device_fingerprint: deviceFingerprint }),
  }, token);
}
