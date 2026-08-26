# Master Engineering Audit, System Architecture & Final-Year Project Defense Guide

## Executive Summary
The **AI-Powered Smart University Digital Ecosystem** is an enterprise-grade digital platform engineered to unify university administration, academic lifecycle management, anti-proxy attendance, student leave workflows, digital identity, personalized learning, career intelligence, and AI-driven campus copilot services into **one single, cohesive SaaS platform**.

Designed specifically as a BTech Final-Year Capstone Project, the platform combines modern micro-modular backend microservices, normalized relational database persistence, zero-trust backend Role-Based Access Control (RBAC), permission-aware AI tool orchestration, and a modern React 19 + TypeScript + Tailwind CSS user interface.

---

## 1. Codebase Audit & Gap Analysis

| Component | Audit State | Target Production & Capstone State |
| :--- | :--- | :--- |
| **Backend API** | FastAPI 0.110 REST Architecture | 8 Modular Routers (`auth`, `academic`, `attendance`, `permissions`, `services`, `notifications`, `ai`, `career`, `campus`). |
| **Database Schema** | 25 Normalized Tables | Full relational schema covering Users, Students, Faculty, Attendance, Anomalies, Permissions, Services, Notifications, RAG Documents, Library, Hostel, Transport, Events, Passports, and AI Messages. |
| **Anti-Proxy Attendance** | 15s Rotating TOTP & Fingerprinting | Layered TOTP tokens, session window locks, device fingerprint collision flags, and manual faculty override workflows. |
| **Permissions & Leaves** | Multi-Tier Workflow + Roll Numbers | Configurable approval (`PENDING` -> `FACULTY_REVIEW` -> `HOD_REVIEW` -> `APPROVED`), proof validation, and automated faculty notifications containing Student Roll Numbers. |
| **AI Layer & Copilot** | 3-Layer Agent Architecture | RAG Knowledge Base retriever, permission-isolated internal tools, local offline fallback model, and external API adapter integration (`AI_PROVIDER`, `AI_API_KEY`). |
| **Frontend UI/UX** | React 19 + TypeScript + Vite | Role-tailored dashboards for Student Portal, Faculty Portal (leave & roll number focus), and Admin Analytics Console. |
| **Testing & CI** | 15 Passing Test Modules | Full automated integration test runner (`run_all_tests.py`) covering security, RBAC, anti-proxy mechanics, AI tool sandboxing, and campus APIs. |

---

## 2. Three-Layer AI Architecture

1. **Layer 1 — Knowledge (University RAG)**:
   - Indexes university regulations, grading policies, attendance requirements, and department FAQs.
   - Provides source document citations for all policy-related queries.
2. **Layer 2 — Tools (Permission-Aware Sandbox)**:
   - Scoped execution wrappers (`get_student_profile`, `get_attendance_summary`, `get_permission_status`, `search_university_rag`).
   - Rejects unauthorized cross-student data access attempts at the backend layer.
3. **Layer 3 — Agent & Orchestration**:
   - Intent classifier detects user needs, selects authorized backend tools, and formats grounded responses.
   - Features a **Local Fallback Mode** (works with zero API key requirement) and supports external LLM adapters (`NVIDIA NeMo`, `GLM-4.7`, `Gemini`, `OpenAI`).

---

## 3. Database Entity Mappings (25 Tables)

1. `users` & `roles`
2. `departments`
3. `students`
4. `faculty`
5. `courses`
6. `classes`
7. `enrollments`
8. `attendance_sessions`
9. `attendance_records`
10. `attendance_anomalies`
11. `permission_requests`
12. `service_requests`
13. `notifications`
14. `knowledge_documents`
15. `audit_logs`
16. `library_books`
17. `library_borrow_records`
18. `hostel_rooms`
19. `hostel_complaints`
20. `transport_routes`
21. `campus_events`
22. `event_registrations`
23. `student_skill_passports`
24. `ai_conversations`
25. `ai_messages`

---

## 4. Final Demonstration Scenario

1. **Student Login**: Student authenticates and views attendance metrics, active class schedules, and Digital ID card.
2. **Leave Application**: Student applies for medical leave; system includes Student Roll Number (`STU2025001`) and sends an `ACTION_REQUIRED` notification to Faculty.
3. **Faculty Portal**: Faculty reviews student leave request displaying student Roll Number for manual attendance reconciliation.
4. **AI Copilot Query**: Student asks "What is my attendance requirement?" -> AI performs RAG retrieval against official university regulations and cites source.
5. **AI Career & Project Lab**: Student generates ATS resume analysis and project SRS blueprint.
6. **Admin Dashboard**: Administrator monitors university-wide metrics, system audit logs, and service SLAs.
