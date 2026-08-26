# BTech Final-Year Project Report: AI-Powered Smart University Digital Ecosystem

## Executive Summary
The **AI-Powered Smart University Digital Ecosystem** is an enterprise-grade digital platform designed to modernize university operations. It integrates academic management, anti-proxy smart attendance, multi-tiered leave permissions, digital service request workflows, secure digital student IDs, and an AI copilot equipped with Retrieval-Augmented Generation (RAG) and permission-aware tool calling.

## 1. Introduction
Traditional university portals suffer from fragmented systems, lack of intelligent automation, static attendance vulnerability to proxy logging, and delayed service turnarounds. This project presents a unified solution addressing these operational challenges.

## 2. Existing System vs. Proposed System
| Feature | Legacy Systems | AI-Powered Smart University Ecosystem |
|---|---|---|
| **Attendance** | Paper register / static QR | Dynamic TOTP QR + Anti-Proxy Anomaly Engine |
| **Permissions** | Paper forms / physical signatures | Configurable multi-tiered digital approval workflow |
| **Services** | Manual office queues | Tokenized service request center with digital artifacts |
| **Student Support** | Static FAQs | Guardrailed AI Copilot with dynamic tool execution & RAG |
| **Career & Projects** | Manual notice boards | AI Job matching, ATS resume scoring, AI Project Mentor |

## 3. System Architecture & Methodology
The platform adopts a decoupled micro-service-ready architecture using FastAPI for the backend API layer and React with TypeScript and Tailwind CSS for the frontend client experience. Data persistence relies on a PostgreSQL relational database with SQLAlchemy ORM, complemented by vector search mechanisms for RAG functionality.

## 4. Key Subsystem Descriptions
1. **Smart Anti-Proxy Attendance Subsystem**: Uses dynamic session tokens, short lifetimes, device fingerprinting, and automated anomaly flagging.
2. **Multi-Tier Permission Engine**: Tracks leave requests across Faculty and HOD review levels with proof verification.
3. **Permission-Aware AI Copilot**: Uses RAG and internal tool execution while maintaining strict user data boundary checks.
4. **AI Project Lab & Career Hub**: Provides automated roadmaps, resume ATS optimization, and project SRS generation.

## 5. Security & Verification
Security is enforced using JWT token rotation, bcrypt password encryption, RBAC FastAPI middleware, dynamic QR token verification, and immutable audit logs.

## 6. Conclusion & Future Scope
The AI-Powered Smart University Digital Ecosystem demonstrates the feasibility of combining enterprise software design with AI technologies to deliver a secure, efficient, and user-centric university environment.
