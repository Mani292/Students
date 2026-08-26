# Security Architecture & AI Safety Guidelines

## 1. Authentication & Session Security
- Passwords are hashed using standard bcrypt/argon2 hashing algorithms.
- JSON Web Tokens (JWT) are signed with short-lived access tokens (15 mins) and long-lived refresh tokens (7 days).
- Automatic token rotation is enforced upon refresh.

## 2. Backend Role-Based Access Control (RBAC)
- Permission checks take place strictly at the backend level through FastAPI dependency injection.
- Role Hierarchy: `SUPER_ADMIN` > `ADMIN` > `HOD` > `FACULTY` > `STUDENT`.
- Endpoint handlers verify both Role and Resource Ownership (e.g., student A cannot view student B's records unless authorized).

## 3. Anti-Proxy Attendance Verification
- Dynamic TOTP seed per active session regenerated every 10–15 seconds to prevent static QR screenshot sharing.
- Client Device Fingerprinting (Browser/Device hash, IP address, user-agent check).
- Geofencing / Location Validation architecture support.
- Automated Anomaly Engine flags duplicate submissions, rapid IP shifts, or abnormal device changes for faculty audit.

## 4. AI Copilot & Tool Security (Guardrails)
- **No Direct DB Access**: The AI model interacts strictly through permission-wrapped tool functions.
- **Context Isolation**: Tool parameters are populated or filtered using the authenticated user's session context.
- **Prompt Injection Defense**: Input sanitization strips system override prompts. System prompts explicitly instruct the AI to refuse unauthorized queries.
- **Source Grounding**: RAG answers must cite verified university knowledge base chunks; missing answers trigger explicit fallback without hallucination.

## 5. Audit Logging & Compliance
- All sensitive operations (Attendance modification, Permission approval/rejection, Role assignments, Service processing) write immutable log entries into `audit_logs`.
