# Database ER Schema Specifications

## Entities and Relationships

### 1. Security & Core User Hierarchy
- `users`: `id`, `email`, `hashed_password`, `full_name`, `role` (`STUDENT`, `FACULTY`, `HOD`, `ADMIN`, `SUPER_ADMIN`), `is_active`, `created_at`
- `students`: `id`, `user_id` (FK), `roll_number`, `department_id` (FK), `year`, `semester`, `cgpa`, `skills` (JSON), `career_interests` (JSON)
- `faculty`: `id`, `user_id` (FK), `employee_id`, `department_id` (FK), `designation`, `specialization`
- `departments`: `id`, `code`, `name`, `hod_id` (FK)

### 2. Academic & Attendance Subsystem
- `courses`: `id`, `code`, `title`, `department_id` (FK), `credits`
- `classes`: `id`, `course_id` (FK), `faculty_id` (FK), `academic_year`, `semester`, `room_number`
- `enrollments`: `id`, `student_id` (FK), `class_id` (FK), `enrolled_at`
- `attendance_sessions`: `id`, `class_id` (FK), `faculty_id` (FK), `session_token`, `start_time`, `end_time`, `is_active`
- `attendance_records`: `id`, `session_id` (FK), `student_id` (FK), `timestamp`, `device_fingerprint`, `status` (`PRESENT`, `ABSENT`, `FLAGGED`)
- `attendance_anomalies`: `id`, `record_id` (FK), `reason`, `severity`, `reviewed_by` (FK), `status`

### 3. Leave & Digital Service Center
- `permissions`: `id`, `student_id` (FK), `reason`, `start_date`, `end_date`, `proof_url`, `status` (`PENDING`, `FACULTY_REVIEW`, `HOD_REVIEW`, `APPROVED`, `REJECTED`)
- `service_requests`: `id`, `student_id` (FK), `service_type` (`BONAFIDE`, `ID_CARD`, `HOSTEL`, `TRANSPORT`), `status`, `details` (JSON), `processed_by` (FK)

### 4. AI & Knowledge Base
- `knowledge_documents`: `id`, `title`, `category`, `source_url`, `created_at`
- `knowledge_chunks`: `id`, `document_id` (FK), `content`, `embedding_id`
- `ai_conversations`: `id`, `user_id` (FK), `title`, `created_at`
- `ai_messages`: `id`, `conversation_id` (FK), `sender`, `content`, `tool_calls` (JSON)

### 5. Audit Logging
- `audit_logs`: `id`, `actor_id` (FK), `action`, `resource`, `timestamp`, `ip_address`, `details` (JSON)
