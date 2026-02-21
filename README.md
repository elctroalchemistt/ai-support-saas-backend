# 🚀 Production-Ready FastAPI SaaS Backend

A secure, scalable backend template designed for launching SaaS products fast.

Built with FastAPI, PostgreSQL, Redis and Docker.
Includes production-grade authentication with refresh token rotation and multi-tenant support.

---

## 🎯 Who Is This For?

- Startup founders building MVPs
- Developers who need secure authentication out of the box
- SaaS products requiring scalable backend architecture
- Teams who want to avoid backend technical debt

---

## ✨ Core Features

- 🔐 JWT Authentication (Access + Refresh)
- 🍪 Secure HttpOnly Cookie auth (+ optional Authorization header)
- 🔄 Refresh token rotation + revocation (replay-attack resistant)
- 🏢 Multi-organization (multi-tenant ready)
- 🐘 PostgreSQL + SQLAlchemy 2.0
- ⚡ Redis (rate limiting / caching ready)
- 🐳 Fully Dockerized (API + Postgres + Redis)
- 🧱 Clean modular architecture
- 🛡 Environment-based configuration

---

## 🏗 Architecture Overview

Client → FastAPI → PostgreSQL  
                    ↓  
                  Redis  
                    ↓  
                 Alembic  

Structured for scalability and production deployment.

---

## ⚡ Quick Start

```bash
git clone https://github.com/elctroalchemistt/ai-support-saas-backend
cd ai-support-saas-backend
docker compose up --build
