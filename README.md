# 🚀 AI Support SaaS API

Production-ready FastAPI backend with JWT auth (access + refresh), refresh token rotation, Postgres, Redis, and Docker.

## ✨ Features
- 🔐 JWT Authentication (Access + Refresh)
- 🍪 Secure HttpOnly Cookie auth (+ optional Authorization header)
- 🔄 Refresh token rotation + revocation (replay-attack resistant)
- 🏢 Multi-organization support
- 🐘 PostgreSQL + SQLAlchemy 2.0
- ⚡ Redis ready (rate-limit / cache)
- 🐳 Dockerized (API + Postgres + Redis)
- 🧱 Clean architecture (routers / models / core / schemas)
- 🛡 Config via environment variables

## 🏗 Tech Stack
FastAPI · SQLAlchemy 2.0 · PostgreSQL · Redis · python-jose (JWT) · bcrypt · Docker Compose

## 📁 Project Structure

## 🔐 Authentication Flow
- **POST** `/auth/signup` → create user + set cookies
- **POST** `/auth/login` → issue access + refresh tokens
- **GET**  `/auth/me` → read access token from cookie or header
- **POST** `/auth/refresh` → validate + rotate refresh token
- **POST** `/auth/logout` → revoke refresh token + clear cookies

## ⚙️ Environment Variables
Create `.env` based on `.env.example`:

```env
ENV=dev
API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/ai_support
REDIS_URL=redis://redis:6379/0

SECRET_KEY=change-me
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

COOKIE_SECURE=false
COOKIE_SAMESITE=lax
CORS_ORIGINS=http://localhost:3000
🐳 Run with Docker
docker compose up -d --build

API:

http://localhost:8000

Docs (Swagger):

http://localhost:8000/docs

🧪 Reset (including DB volume)
docker compose down -v
docker compose up -d --build
🔒 Security Notes

Refresh tokens are stored in DB (hashed)

Rotation + revocation prevents replay

HttpOnly cookies mitigate XSS token theft

🚀 Production Checklist

Use HTTPS

Set COOKIE_SECURE=true

Strong SECRET_KEY

Strict CORS_ORIGINS

Add migrations (Alembic), rate limiting, logging/monitoring

📌 Roadmap

RBAC

Email verification + password reset

Tenant isolation hardening

Background jobs (RQ/Celery)

👨‍💻 Author

Electro Mage