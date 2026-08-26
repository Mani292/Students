# API Specifications

## Base URL: `/api/v1`

### Authentication & Authorization
- `POST /auth/login` - User login with credentials, returns JWT access and refresh token.
- `POST /auth/register` - Create a student account with a validated profile. Roles are assigned server-side.
- `POST /auth/refresh` - Refresh access token using refresh token.
- `GET /auth/me` - Get current user profile and role details.

### Academic & Student APIs
- `GET /students/me/dashboard` - Get student dashboard overview (attendance stats, upcoming classes, service requests, AI suggestions).
- `GET /students/me/digital-id` - Get digital ID card details and dynamic verification token.
- `GET /verify/digital-id/{token}` - Public endpoint to verify digital ID token and display safe minimum profile info.

### Smart Attendance APIs
- `POST /attendance/session/start` (Faculty) - Launch interactive attendance session with dynamic TOTP/QR code.
- `POST /attendance/session/close` (Faculty) - Manually close attendance session.
- `POST /attendance/record` (Student) - Record attendance using session token and client fingerprinting.
- `GET /attendance/anomalies` (Faculty/Admin) - View flagged anti-proxy attendance anomalies.
- `PATCH /attendance/anomalies/{id}` (Faculty/Admin) - Resolve or confirm attendance anomaly flag.

### Permission & Leave Workflow
- `POST /permissions/apply` (Student) - Apply for leave/permission with optional proof document.
- `GET /permissions/my-requests` (Student) - View personal permission history.
- `GET /permissions/pending` (Faculty/HOD) - View permissions pending review.
- `POST /permissions/{id}/action` (Faculty/HOD) - Approve, reject, or request clarification on permission.

### Digital Service Center
- `POST /services/request` (Student) - Submit service request (Bonafide, ID card, Hostel, Transport).
- `GET /services/my-requests` (Student) - View status of submitted service requests.
- `PATCH /services/{id}/process` (Admin/Staff) - Update status and issue digital documents.

### AI Copilot & Knowledge Engine
- `POST /ai/chat` (Authenticated User) - Interactive prompt with RAG retrieval and tool calling.
- `POST /ai/learning-path` (Student) - Generate personalized skill roadmap.
- `POST /ai/resume-analysis` (Student) - Analyze resume text against job descriptions for ATS match score and suggestions.
- `POST /ai/project-mentor` (Student) - Generate project SRS, DB Schema, and milestone breakdown.
