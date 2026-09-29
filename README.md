# AI-Powered Smart University Digital Ecosystem

An end-to-end, unified digital platform for higher education institutions that connects students, faculty, and administrators. The ecosystem integrates academic management, anti-proxy attendance, multi-tier permission workflows, AI-assisted learning pathways, placement and career management, and comprehensive campus services into role-based portals.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Method 1: Docker Compose (Recommended)](#method-1-docker-compose-recommended)
  - [Method 2: Local Development Setup](#method-2-local-development-setup)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Documentation Index](#-documentation-index)
- [License](#-license)

---

## ✨ Key Features

### 🎓 Student Portal
- **Attendance Monitoring**: Real-time subject-wise tracking, attendance history, shortages, and dynamic TOTP anti-proxy attendance marking.
- **Permission Requests**: Digital workflow for leave/out-pass requests with real-time status tracking and history.
- **ATS Resume Analyzer**: Automated resume scoring against job descriptions, keyword identification, and optimization recommendations.
- **Structured Learning Tracks**: Personalized skill paths, topic coverage, practice quizzes, and AI recommendations.
- **AI Learning Copilot**: Interactive academic assistant with guardrailed institutional knowledge retrieval (RAG).
- **Placement Tracker**: Real-time job opportunity tracking, application status pipeline, and interview updates.
- **Campus Ecosystem Services**: Integrated digital access for Library, Hostel, Transport, Campus Events, and Skill Passport.

### 👩‍🏫 Faculty Portal
- **Attendance Management**: Mark, edit, and review attendance records with session fingerprinting and anti-proxy validation.
- **Permission Approvals**: Multi-tier review and actioning of student leave/out-pass requests with roll-number reconciliation.
- **Topic Allocation**: Units and curriculum coverage management for assigned subjects.
- **Academic Activity Feed**: Broadcast announcements, tasks, schedules, and class updates.
- **Student Insights**: Authorized access to student academic history and performance metrics.

### 🛡️ Admin Portal & Security
- **User & Role Management**: RBAC with strict scope enforcement across `STUDENT`, `FACULTY`, `HOD`, `ADMIN`, and `SUPER_ADMIN`.
- **Academic Configuration**: Manage departments, branches, academic years, semesters, sections, and subjects.
- **Audit Logging**: Immutable event recording for role changes, attendance modifications, and policy approvals.
- **Knowledge & AI Configuration**: Control institutional knowledge sources, vector search policies, and AI tool sandboxes.

---

## 🏗️ System Architecture

```
                                  [ CLIENT LAYER ]
      ┌──────────────────┬───────────────────┬───────────────────┬──────────────────┐
      │  Student Portal  │  Faculty Portal   │  Admin Dashboard  │ Mobile / Web UI  │
      └────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────┬────────┘
               │                   │                   │                   │
               └───────────────────┼───────────────────┴───────────────────┘
                                   │ HTTPS / REST API
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
 ├── Campus Services           ├── Digital ID Generator       ├── Guardrailed Tool System
 └── Audit Logger              └── Notifications              └── Skill & Placement Lab
       │                              │                              │
       └──────────────────────────────┼──────────────────────────────┘
                                      │
                                      ▼
                                [ DATA LAYER ]
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  PostgreSQL / SQLite           Redis (Cache / Session)        MongoDB Atlas / Vector DB
```

---

## 💻 Tech Stack

- **Backend**: Python 3.12+, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy ORM](https://www.sqlalchemy.org/), Pydantic v2, PyJWT, Passlib (Bcrypt), Motor (MongoDB Async)
- **Frontend**: [React 18](https://react.dev/), TypeScript, [Vite](https://vitejs.dev/), Tailwind CSS, Lucide Icons, Recharts
- **Database**: PostgreSQL / SQLite (Development & Testing), Redis (Caching & Sessions), Vector Embeddings / MongoDB
- **DevOps & Infrastructure**: Docker, Docker Compose, Nginx reverse proxy support

---

## 📁 Project Directory Structure

```text
.
├── backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/             # API Endpoints (auth, academic, attendance, campus, ai, etc.)
│   │   ├── core/               # App configuration, security, JWT, RBAC, logging
│   │   ├── db/                 # Database initialization, session management, MongoDB connection
│   │   ├── models/             # SQLAlchemy ORM schemas & domain models
│   │   └── services/           # Business logic, AI RAG engine, notifications
│   ├── run_all_tests.py        # Centralized backend test suite runner
│   └── requirements.txt        # Python backend dependencies
├── frontend/                   # React + TypeScript + Vite Frontend Application
│   ├── src/
│   │   ├── components/         # Reusable UI components & layouts
│   │   ├── pages/              # Role-based portal views (Student, Faculty, Admin, Campus)
│   │   ├── services/           # API integration clients
│   │   └── types/              # TypeScript type definitions
│   └── package.json            # Node.js frontend dependencies & scripts
├── docs/                       # Comprehensive Architecture & Technical Specifications
│   ├── ARCHITECTURE.md         # System design, data flow, security model
│   ├── PRODUCT_SPECIFICATION.md# Complete product modules and roadmap
│   ├── API_SPEC.md             # REST API routes and data contracts
│   ├── DATABASE_SCHEMA.md      # Database entities and relations
│   ├── DEPLOYMENT.md           # Deployment strategies (Docker, VPS, Reverse Proxy)
│   ├── AUDIT.md                # System audit, engineering standards, presentation guides
│   ├── SECURITY.md             # RBAC, TOTP, and security architecture
│   └── PROJECT_REPORT.md       # Capstone project report & summary
├── docker-compose.yml          # Container orchestration for local / production dev
└── .env.example                # Example configuration environment variables
```

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.12 or later
- **Node.js**: v18 or later (with `npm`)
- **Docker & Docker Compose**: (Optional, for containerized execution)

---

### Method 1: Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Setup environment variables**:
   ```bash
   cp .env.example .env
   ```

3. **Spin up services with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - **Frontend**: [http://localhost:3000](http://localhost:3000) (or port `5173`)
   - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Method 2: Local Development Setup

#### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment settings
cp ../.env.example .env

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API will be available at `http://localhost:8000`. Swagger API documentation is available at `http://localhost:8000/docs`.

#### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend will be available at `http://localhost:5173` (or `http://localhost:3000`).

---

## ⚙️ Configuration & Environment Variables

Key environment settings configured via `.env`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | Relational database connection string | `sqlite:///./backend/smart_university.db` |
| `JWT_SECRET` | Secret key for JWT signature validation | `replace-with-a-long-random-secret` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | `30` |
| `AI_PROVIDER` | AI provider configuration (`local`, `openai`, etc.) | `local` |
| `AI_MODEL` | AI model name | `glm-4.7` |
| `CORS_ORIGINS` | Allowed origins for cross-origin requests | `http://localhost:3000,http://localhost:5173` |

---

## 🧪 Testing & Quality Assurance

### Run Backend Integration & Unit Tests
To execute all backend tests (Auth, Attendance, Permissions, Campus, RAG, RBAC, Security):

```bash
python3 backend/run_all_tests.py
```

Or run test suites individually using `pytest`:

```bash
cd backend
pytest test_auth.py test_attendance.py test_permissions.py test_campus.py test_rbac.py
```

### Run Frontend Build & Lint Verification

```bash
cd frontend
npm run build
```

---

## 📚 Documentation Index

For detailed specifications, architectural diagrams, and deployment protocols, refer to the `docs/` directory:

- 📑 [Product Specification](docs/PRODUCT_SPECIFICATION.md)
- 🏗️ [Architecture & Technical Specifications](docs/ARCHITECTURE.md)
- 🔌 [API Specifications](docs/API_SPEC.md)
- 🗄️ [Database Schema Reference](docs/DATABASE_SCHEMA.md)
- 🚀 [Deployment Guide](docs/DEPLOYMENT.md)
- 🛡️ [Security Architecture](docs/SECURITY.md)
- 📊 [Master Audit & Presentation Guide](docs/AUDIT.md)
- 📝 [Project Report](docs/PROJECT_REPORT.md)

---

## 📄 License

This project is open-source under the MIT License.
