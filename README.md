# AA Virtual Group Platform

> *Anonymous-first meetings directory + join flow with secure hosting, moderation tools, and simple treasury management*

A modern, privacy-focused platform for Alcoholics Anonymous virtual meetings, built with Next.js frontend, FastAPI backend, and PostgreSQL database. Designed for secure, auditable operations with minimal maintenance overhead.

## 🎯 Goals

- **Anonymous-first meetings directory** with secure join flow
- **Secure hosting & moderation tools** for virtual meeting management
- **Simple, auditable treasury** (budget, contributions, expenses)
- **Low-ops deployment** with Vercel + managed Postgres

## 🏗️ Architecture

```mermaid
graph TB
    Browser[Browser] --> NextJS[Next.js App Router on Vercel]
    NextJS --> Edge[Edge Middleware]
    NextJS --> Backend[FastAPI Backend]
    NextJS --> DB[(Postgres Database)]
    Backend --> DB
    Backend --> Redis[(Redis Cache)]
    Backend --> S3[S3 Storage]
    
    Edge --> Auth[Auth Cookie/JWT Check]
    Edge --> Rate[Rate Limiting]
    
    Backend --> AuthAPI[Auth APIs]
    Backend --> MeetingAPI[Meeting APIs]
    Backend --> TreasuryAPI[Treasury APIs]
    Backend --> ModAPI[Moderation APIs]
```

### High-level Architecture

```
[Browser]
│
├─ Next.js (App Router) on Vercel
│    ├─ Edge Middleware: auth cookie/jwt check, rate limiting
│    └─ Server Actions / API routes (thin proxy)
│
├─────────────▶ FastAPI Backend (Python)
│                ├─ Auth (JWT / Magic links)
│                ├─ REST/JSON APIs
│                ├─ Alembic migrations
│                └─ Background tasks (APScheduler / provider cron)
│
└─────────────▶ Postgres (Vercel Postgres / Neon)
```

## 🛠️ Tech Stack

### Frontend
- **Next.js 14+** with App Router
- **React Server Components** for optimal performance
- **TypeScript** for type safety
- **Tailwind CSS** + **shadcn/ui** for modern UI
- **next-intl** for internationalization
- **Zod** for runtime validation

### Backend
- **Python 3.11** with FastAPI
- **Pydantic v2** for data validation
- **SQLAlchemy 2.0** for database ORM
- **Alembic** for database migrations
- **Uvicorn** as ASGI server

### Authentication
- **Passwordless magic links** + optional OAuth (Google/Apple)
- **JWT tokens** with short-lived access (15m) and refresh (7d)
- **httpOnly cookies** for secure session management
- **Token rotation** and revocation list in Redis

### Infrastructure
- **Database**: Postgres 15+ (managed: Vercel Postgres/Neon)
- **Cache/Rate-limit**: Upstash Redis (or Vercel KV)
- **Storage**: S3-compatible bucket (R2/S3) with signed URLs
- **Telemetry**: OpenTelemetry → OTLP (Axiom/Datadog)
- **CI/CD**: GitHub → Vercel (frontend), GitHub Actions (backend)

## 📁 Project Structure

```
aa-virtual/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── page.tsx     # Home + search
│   │   │   ├── meetings/    # Meeting directory & details
│   │   │   ├── join/        # Anonymous join flow
│   │   │   ├── my/          # Profile/Preferences
│   │   │   └── service/     # Service dashboard
│   │   │       ├── treasury/ # Budget & contributions
│   │   │       └── reports/  # Financial reports
│   │   └── components/      # Reusable UI components
│   ├── middleware.ts        # Edge middleware for auth/rate limiting
│   └── package.json
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── endpoints/
│   │   │       ├── auth.py          # Authentication
│   │   │       ├── meetings.py      # Meeting management
│   │   │       ├── treasury.py      # Financial operations
│   │   │       └── moderation.py    # Meeting moderation
│   │   ├── core/           # Configuration & security
│   │   ├── db/             # Database setup & sessions
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/smcnary/aa-virtual.git
   cd aa-virtual
   ```

2. **Install dependencies**
   ```bash
   npm run setup
   ```

3. **Set up environment variables**
   ```bash
   # Copy example environment files
   cp env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   
   # Edit the files with your configuration
   ```

4. **Start the development environment**
   ```bash
   # Using Docker (recommended)
   npm run docker:dev
   
   # Or run locally
   npm run dev
   ```

5. **Initialize the database**
   ```bash
   npm run db:init
   npm run db:migrate
   npm run db:seed
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔐 Authentication & Security

### Magic Link Authentication
```typescript
// Frontend: Request magic link
const requestMagicLink = async (email?: string) => {
  const res = await fetch('/api/auth/magic-link', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return res.json();
};
```

### JWT Token Management
- **Access tokens**: 15-minute expiry
- **Refresh tokens**: 7-day expiry with rotation
- **Revocation**: Blacklist in Redis for immediate invalidation
- **Rate limiting**: Per-user and per-endpoint limits

### Privacy & Security Features
- **PII minimization**: No IP storage; salted fingerprint hashes for rate limiting
- **TLS only**: HSTS headers, secure cookies
- **CSRF protection**: SameSite=Lax cookies, JSON-only APIs
- **Input validation**: Zod schemas on frontend, Pydantic on backend

## 📊 API Design

### Authentication
```
POST /auth/magic-link     → Send sign-in link
GET  /auth/callback       → Exchange token → JWT + refresh cookie
POST /auth/refresh        → Rotate tokens
POST /auth/logout         → Invalidate tokens
```

### Meetings
```
GET  /meetings?public=1&tz=America/Chicago&from=...&to=...
POST /meetings            (role: secretary/host)
GET  /meetings/{id}       / PATCH /meetings/{id}
GET  /meetings/{id}/occurrences?range=...
POST /occurrences/{id}/start|end|cancel (host/tech)
```

### Attendance & Communication
```
POST /occurrences/{id}/join     (guest or user; passcode hashed compare)
POST /occurrences/{id}/chat     (ephemeral; retention policy)
POST /moderation/{occurrenceId} (mute/remove/ban)
```

### Budget & Treasury
```
GET  /treasury/accounts                    / POST /treasury/accounts
POST /treasury/contributions/batch         (link to meeting/occurrence)
POST /treasury/expenses                    → approve → pay (workflow)
GET  /treasury/budget/fy/{fiscalYearId}/vaa → v_budget_vs_actual view
POST /treasury/journal/entries             (+ splits)
GET  /treasury/balances                    → v_account_balance
```

### Attachments
```
POST /attachments/sign     → Pre-signed PUT URL
POST /attachments/confirm  → Persist metadata row
```

## 💰 Treasury Management

### Chart of Accounts
```
1000 - Checking Account
4100 - Seventh Tradition (Contributions)
4200 - Service Contributions
5200 - Rent & Utilities
5300 - Literature & Supplies
5400 - Service Work Expenses
```

### Workflow
1. **Contributions**: Batch entry linked to meeting/occurrence
2. **Expenses**: Claim → Approval → Payment workflow
3. **Budget**: Fiscal year planning with variance reporting
4. **Reporting**: Real-time balances and budget vs. actual

### Example Contribution Batch
```typescript
const createContributionBatch = async (payload: ContributionBatchPayload) => {
  const res = await fetch(`${process.env.BACKEND_BASE_URL}/treasury/contributions/batch`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json', 
      'Authorization': await getBearer(),
      'Idempotency-Key': generateIdempotencyKey()
    },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to save batch');
  return res.json();
};
```

## 🚀 Deployment

### Vercel (Frontend)
```json
{
  "functions": {
    "app/(api)/**": {
      "maxDuration": 10
    }
  },
  "redirects": [
    { "source": "/healthz", "destination": "/api/healthz", "permanent": false }
  ],
  "crons": [
    { "path": "/api/ops/materialize", "schedule": "0 3 * * *" },
    { "path": "/api/ops/purge", "schedule": "0 4 * * *" }
  ]
}
```

### Backend Options

**Option A: Vercel Serverless Functions (Python)**
- Great for stateless APIs (no WebSockets/long jobs)
- Single vendor, instant previews
- Limited duration & no background threads

**Option B: Container Host (Railway/Fly/Render) - Recommended**
- Dockerfile with Uvicorn workers
- Health checks, autoscaling
- APScheduler for periodic jobs

### Database
- **Vercel Postgres** or **Neon** with connection pooling
- Separate databases per environment (prod, preview, dev)
- Automated backups and point-in-time recovery

### Storage
- **S3/R2 bucket** with signed URLs only
- File uploads for receipts and attachments
- Retention policies for ephemeral content

## 🔧 Environment Configuration

### Frontend (Vercel)
```env
NEXT_PUBLIC_APP_NAME=AA Virtual
NEXT_PUBLIC_BACKEND_URL=https://api.example.com
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=https://your-domain.com
```

### Backend
```env
DATABASE_URL=postgres://user:pass@host:port/db
REDIS_URL=rediss://user:pass@host:port
JWT_ISSUER=https://api.example.com
JWT_AUDIENCE=aa-virtual
JWT_SIGNING_KEY=your-signing-key
EMAIL_SENDER=noreply@example.com
EMAIL_PROVIDER_API_KEY=your-api-key
S3_BUCKET=aa-virtual-prod
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
```

## 🧪 Testing Strategy

### Unit Tests
- Models and services (budget math, JE balancing)
- Contract tests with OpenAPI schema validation
- Zod validators on the client

### Integration Tests
- Database operations with test containers
- API endpoint testing with FastAPI TestClient
- Authentication flow testing

### E2E Tests (Playwright)
- Guest join flow
- Contribution batch entry
- Expense approval workflow
- Budget vs. actual report generation

### Data Integrity Tests
- Journal entry double-entry balancing
- Foreign key constraint validation
- Business rule enforcement

## 📈 Observability

### Tracing
- **OpenTelemetry** in both Next.js and FastAPI
- Request tracing across services
- Database query performance monitoring

### Metrics
- Request latency and throughput
- Database connection pool usage
- Rate limit hit rates
- Treasury operation success rates

### Logging
- Structured JSON logs (Pino for Next.js, stdlib for FastAPI)
- No sensitive data in logs (PII, message contents)
- Log aggregation with Axiom/Datadog

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v
      - name: Run migrations
        run: |
          cd backend
          alembic upgrade head
```

### Deployment Strategy
1. **Frontend**: Vercel automatic deployment on push to main
2. **Backend**: GitHub Actions builds and deploys container
3. **Database**: Alembic migrations run automatically on deployment
4. **Rollback**: Vercel instant revert, backend container rollback

## 🛡️ Security & Privacy

### Data Protection
- **Anonymization**: No IP storage, minimal PII collection
- **Encryption**: TLS 1.3 for transit, AES-256 for sensitive data at rest
- **Access Control**: RBAC with service assignments (host/secretary/treasurer)
- **Audit Trail**: All financial operations logged with user attribution

### Meeting Security
- **Passcode Protection**: Hashed passcodes with salt
- **Moderation Tools**: Mute, remove, ban capabilities
- **Rate Limiting**: Per-user and per-endpoint limits
- **Content Retention**: Ephemeral chat with configurable retention

### Financial Security
- **Double-Entry Bookkeeping**: All transactions balance to zero
- **Approval Workflows**: Multi-step approval for expenses
- **Audit Reports**: Comprehensive financial reporting
- **Idempotency**: All money-affecting operations are idempotent

## 📚 Development Commands

```bash
# Install all dependencies
npm run setup

# Start development servers
npm run dev

# Start with Docker
npm run docker:dev

# Database operations
npm run db:init          # Create initial migration
npm run db:migrate       # Run migrations
npm run db:reset         # Reset database
npm run db:seed          # Seed with sample data

# Testing
npm run test             # Run all tests
npm run test:e2e         # Run E2E tests
npm run test:coverage    # Run with coverage

# Build for production
npm run build

# Start production
npm run docker:prod

# Linting and formatting
npm run lint             # ESLint + Prettier
npm run typecheck        # TypeScript check
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`npm run test`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards
- **TypeScript**: Strict mode enabled
- **Python**: Black formatting, flake8 linting
- **Testing**: 80%+ coverage requirement
- **Documentation**: Update README for new features

## 📞 Support & Contact

### Technical Support
- **Issues**: [GitHub Issues](https://github.com/smcnary/aa-virtual/issues)
- **Documentation**: This README and inline code comments
- **Email**: awakeningnstulsa@gmail.com

### AA Support
- **Official AA**: [aa.org](https://www.aa.org/)
- **Local Meetings**: Find meetings in your area
- **Crisis Support**: Call your sponsor or local AA helpline

## 📄 License & Disclaimer

This project is for educational and service purposes. All A.A. literature and materials are copyrighted by Alcoholics Anonymous World Services, Inc.

**This is not an official Alcoholics Anonymous website.** For official A.A. information, please visit [aa.org](https://www.aa.org/).

## 🙏 Meeting Information

- **Time**: Daily at 7:00 a.m. Central Time
- **Platform**: FreeConferenceCall.com
- **Online Link**: https://join.freeconferencecall.com/timhwalton
- **Phone**: (951) 799-9267
- **Meeting ID**: timhwalton

---

*"Our primary purpose is to stay sober and to help others recover from alcoholism."*

**The Twelve Steps, Twelve Traditions, and all other A.A. literature are copyrighted by A.A. World Services, Inc.**