# Architecture & Technical Specifications

## 1. System Overview
The **AI-Powered Smart University Digital Ecosystem** is a unified digital platform for higher education institutions connecting students, faculty, administrators, academic services, and AI assistants.

## 2. High-Level Architecture

```
                                  [ CLIENT LAYER ]
      ┌──────────────────┬───────────────────┬───────────────────┬──────────────────┐
      │  Student Portal  │  Faculty Portal   │  Admin Dashboard  │ Mobile (Expo/RN) │
      └────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────┬────────┘
               │                   │                   │                   │
               └───────────────────┼───────────────────┴───────────────────┘
                                   │ HTTPS / REST / WebSockets
                                   ▼
                            [ API GATEWAY ]
               ┌──────────────────────────────────────────────┐
               │  FastAPI Router, Auth Middleware & RBAC Core │
               └──────────────────────┬───────────────────────┘
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
[ CORE MODULES ]              [ SMART SERVICES ]             [ AI INTEGRATION ]
 ├── Auth & Users              ├── Anti-Proxy Attendance      ├── GLM-4.7 Copilot
 ├── Academic Rosters          ├── Multi-Tier Permissions     ├── RAG Vector Pipeline
 ├── Service Requests          ├── Digital ID Generator       ├── Guardrailed Tool System
 └── Audit Logger              └── Notifications              └── Skill & Project Lab
       │                              │                              │
       └──────────────────────────────┼──────────────────────────────┘
                                      │
                                      ▼
                                [ DATA LAYER ]
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  PostgreSQL (Relational DB)    Redis (Cache/Session)      Vector Store (FAISS/Chroma)
```

## 3. Technology Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT, Passlib (Bcrypt).
- **Database**: PostgreSQL (SQLite fallback for dev/testing), Redis for caching and session state.
- **AI & RAG**: Vector Embeddings, RAG retriever engine, Tool execution sandbox, Guardrails.
- **DevOps**: Docker, Docker Compose.

## 4. Key Security Mechanisms
- Role-Based Access Control (RBAC) with backend enforcement (`STUDENT`, `FACULTY`, `HOD`, `ADMIN`, `SUPER_ADMIN`).
- Smart Anti-Proxy Attendance: Dynamic TOTP token generation, session fingerprinting, device validation, time-window verification, duplicate flag detection.
- Audit Logging: Immutable recording of critical actions (role changes, attendance updates, permission approvals, document requests).
