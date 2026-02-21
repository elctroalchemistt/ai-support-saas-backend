🚀 AI Support SaaS API

Production-ready FastAPI SaaS backend with JWT authentication, refresh token rotation, PostgreSQL, Redis, Docker, and Alembic.

Built as a scalable multi-tenant backend template for real-world SaaS applications.

📸 Demo
Swagger UI

You can test the API locally via:

http://localhost:8000/docs
✨ Features

🔐 JWT Authentication (Access + Refresh Tokens)

🔄 Refresh Token Rotation + Revocation (Replay Attack Resistant)

🍪 Secure HttpOnly Cookie Auth

🏢 Multi-Organization (Multi-Tenant) Support

🎫 Ticket System with Messages

🧠 Role-based message types (user / agent / ai)

🐘 PostgreSQL + SQLAlchemy 2.0

⚡ Redis Ready (caching / rate limiting)

🐳 Fully Dockerized

🔄 Alembic Database Migrations

🧱 Clean Architecture (routers / models / services / core)

🏗 Tech Stack

FastAPI

SQLAlchemy 2.0

PostgreSQL

Redis

Alembic

python-jose (JWT)

bcrypt

Docker & Docker Compose

🏛 Architecture Overview
apps/api/
│
├── app/
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── schemas/
│   └── main.py
│
├── alembic/
│
└── Dockerfile

Designed using clean separation of concerns:

API Layer (routers)

Business Logic (services)

Data Layer (models)

Configuration (core)

🔐 Authentication Flow
1️⃣ Signup

POST /auth/signup

Creates user

Issues access token

Issues refresh token

Sets secure HttpOnly cookies

2️⃣ Login

POST /auth/login

Validates credentials

Issues new access + refresh tokens

3️⃣ Get Current User

GET /auth/me

Reads access token from:

HttpOnly cookie

OR Authorization header

4️⃣ Refresh Token

POST /auth/refresh

Validates refresh token

Checks revocation

Rotates token

Issues new access token

5️⃣ Logout

POST /auth/logout

Revokes refresh token

Clears cookies

🎫 Ticket System

Create ticket

Update ticket

Add message

Track status & priority

Multi-tenant isolation

Message roles supported:

user

agent

ai

⚙️ Environment Variables

Create a .env file inside apps/api/:

ENV=prod
API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=postgresql+psycopg://app:app@postgres:5432/aisupport
REDIS_URL=redis://redis:6379/0

SECRET_KEY=change-me
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

COOKIE_SECURE=false
COOKIE_SAMESITE=lax

CORS_ORIGINS=["http://localhost:3000"]
🐳 Run Locally
docker compose up -d

Run migrations:

docker compose exec api python -m alembic upgrade head

Access Swagger:

http://localhost:8000/docs
🔒 Security Considerations

Refresh tokens stored in DB

Token rotation prevents replay attacks

HttpOnly cookies prevent XSS token theft

Designed for HTTPS deployment

Multi-tenant isolation

🚀 Use Cases

This backend can be extended into:

AI Customer Support SaaS

Helpdesk System

Multi-tenant CRM Backend

SaaS MVP Template

Startup Boilerplate

📈 Future Improvements

Role-based access control (RBAC)

API key authentication

Email verification

Password reset flow

Rate limiting via Redis

OpenAI integration for AI support replies

Admin dashboard frontend

## 📸 Demo

![Swagger UI](assets/swagger.png)
👨‍💻 Author

Built with ❤️ using FastAPI and modern Python stack
