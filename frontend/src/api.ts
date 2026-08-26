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

export async function login(email: string, password: string): Promise<{ token: string; user: SessionUser }> {
  const session = await request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const user = await request<SessionUser>('/auth/me', {}, session.access_token);
  return { token: session.access_token, user };
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

export function recordAttendance(token: string, sessionToken: string, totpCode: string, deviceFingerprint: string) {
  return request<{ status: string }>('/attendance/record', {
    method: 'POST',
    body: JSON.stringify({ session_token: sessionToken, totp_code: totpCode, device_fingerprint: deviceFingerprint }),
  }, token);
}
