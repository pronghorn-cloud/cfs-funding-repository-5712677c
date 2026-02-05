# CFS Funding Portal + Social Vulnerability Index

Full-stack web application for the Government of Alberta Community Facilities and Supports (CFS) shelter funding management, integrated with a Social Vulnerability Index (SVI) for data-driven funding decisions.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Vue 3, Vite, TypeScript, Pinia, GoA Design System (`@abgov/web-components`), Tailwind CSS |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy (async), asyncpg |
| **Database** | PostgreSQL 16 |
| **Auth** | Azure AD (MSAL) + application-issued JWTs |
| **Storage** | Azure Blob Storage (documents, reports) |
| **Maps** | Leaflet (`@vue-leaflet/vue-leaflet`) |
| **Charts** | Chart.js (`vue-chartjs`) |
| **Monitoring** | structlog (JSON), Prometheus metrics, circuit breakers |
| **Infrastructure** | Docker Compose (PostgreSQL, Redis, Azurite) |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory, lifespan, middleware
│   │   ├── config.py                  # Pydantic Settings (env-based)
│   │   ├── database.py                # Async SQLAlchemy engine + session
│   │   ├── exceptions.py              # Custom exceptions + handlers
│   │   ├── middleware/                 # Correlation ID, request logging, rate limiting
│   │   ├── auth/                      # Azure AD MSAL + JWT auth
│   │   ├── organizations/             # Shelter organization CRUD
│   │   ├── applications/              # Funding application workflow
│   │   ├── documents/                 # Azure Blob Storage file management
│   │   ├── reviews/                   # Reviewer scoring + comparison
│   │   ├── vulnerability/             # SVI scores, heatmap, engine
│   │   ├── ingestion/                 # Data source adapters + pipeline
│   │   ├── geography/                 # Regions, municipalities, GeoJSON
│   │   ├── reporting/                 # PDF/DOCX briefing generation
│   │   ├── notifications/             # Email via Azure Communication Services
│   │   ├── health/                    # Kubernetes-style probes
│   │   └── common/                    # Pagination, circuit breaker, metrics, audit
│   ├── alembic/                       # Database migrations
│   ├── tests/                         # pytest test suite
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── router/                    # Vue Router with role-based auth guards
│   │   ├── stores/                    # Pinia stores (7 modules)
│   │   ├── services/                  # Typed API services (Axios)
│   │   ├── layouts/                   # Default, Auth, Admin layouts
│   │   ├── views/                     # 16 views across 6 route groups
│   │   ├── composables/               # useAuth, usePagination
│   │   ├── types/                     # TypeScript interfaces
│   │   └── assets/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
└── .gitignore
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose

## Getting Started

### 1. Start Infrastructure Services

```bash
cd backend
docker-compose up -d postgres redis azurite
```

This starts PostgreSQL (port 5432), Redis (port 6379), and Azurite (ports 10000-10002).

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env with your Azure AD credentials

# Run database migrations
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/api/docs` (debug mode only).

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend will be available at `http://localhost:5173` with API requests proxied to the backend.

### 4. Full Stack via Docker

```bash
cd backend
docker-compose up
```

This starts all services including the backend (port 8000). Run the frontend separately with `npm run dev`.

## API Overview

All API routes are under `/api/v1` except health checks.

| Module | Endpoints | Auth |
|--------|-----------|------|
| **Health** | `GET /health/live`, `/health/ready`, `/health/startup` | Public |
| **Auth** | `GET /auth/login`, `/auth/callback`, `POST /auth/refresh`, `/auth/logout`, `GET /auth/me` | Mixed |
| **Organizations** | CRUD at `/organizations` | Authenticated |
| **Applications** | CRUD + sections + status workflow at `/applications` | Authenticated |
| **Documents** | Upload/download at `/documents` | Authenticated |
| **Reviews** | Scoring + comparison at `/reviews` | Reviewer, Admin |
| **Vulnerability** | Scores, heatmap, compare, indicators at `/vulnerability` | Reviewer, Admin |
| **Ingestion** | Trigger + status at `/ingestion` | Admin |
| **Geography** | Regions, municipalities, GeoJSON at `/geography` | Authenticated |
| **Reports** | Briefing generation at `/reports` | Admin |

## Application Workflow

```
Draft → Submitted → Under Review → Reviewed → Recommended → Approved
                  ↘                ↗            ↘
            Additional Info Requested              Denied
```

## Social Vulnerability Index

The SVI engine scores regions across Alberta using 83 indicators in 6 categories:

| Category | Description |
|----------|-------------|
| Socioeconomic | Income, employment, education, poverty |
| Demographic | Age distribution, Indigenous population, immigration |
| Health | Life expectancy, chronic disease, mental health, substance use |
| Housing | Affordability, homelessness, housing condition, overcrowding |
| Infrastructure | Service access, transportation, broadband connectivity |
| Environmental | Flood risk, wildfire exposure, air quality, climate vulnerability |

**Scoring:**
1. **Normalize** each indicator across regions (min-max, z-score, or percentile)
2. **Category scores** = weighted average of normalized indicators (0-100)
3. **Composite SVI** = weighted sum of category scores (0-100)
4. **KPMG Grade**: A (0-20), B (20-40), C (40-60), D (60-80), E (80-100)
5. **Risk Index** = 0.4 × Vulnerability + 0.2 × Resources + 0.2 × Pressure + 0.2 × Funding

### Data Sources

| Source | Adapter | Data |
|--------|---------|------|
| Statistics Canada | `statscan` | Census, income, employment |
| GoA Health | `goa_health` | Health outcomes, service utilization |
| Environics Analytics | `environics` | Demographic projections |
| CFS Internal | `cfs_internal` | Shelter capacity, funding history |
| SCSS | `scss` | Shelter occupancy statistics |
| Recovery Alberta | `recovery_alberta` | Disaster impact data |
| Justice | `justice` | Crime, safety indicators |

## Frontend Routes

| Path | View | Roles |
|------|------|-------|
| `/` | Landing Page | Public |
| `/login` | Login (Azure AD) | Public |
| `/dashboard` | Applicant Dashboard | All authenticated |
| `/applications/new` | Multi-step Application Form | Applicant |
| `/applications/:id` | Application Detail | All authenticated |
| `/reviews` | Reviewer Dashboard | Reviewer, Admin |
| `/reviews/:appId` | Application Scoring | Reviewer, Admin |
| `/reviews/compare` | Application Comparison | Reviewer, Admin |
| `/vulnerability` | SVI Heatmap (Leaflet) | Reviewer, Admin |
| `/vulnerability/compare` | Region Comparison | Reviewer, Admin |
| `/vulnerability/indicators` | Indicator Explorer | Reviewer, Admin |
| `/vulnerability/data-sources` | Data Source Management | Admin |
| `/reports` | Report Generator | Admin |
| `/admin` | Admin Dashboard | Admin |
| `/admin/users` | User Management | Admin |
| `/admin/config` | System Configuration | Admin |

## Running Tests

```bash
cd backend
pytest                      # Run all tests
pytest tests/test_svi_engine.py  # SVI engine tests only
pytest --cov=app            # With coverage
```

## Environment Variables

See `backend/.env.example` for the full list. Key variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `AZURE_TENANT_ID` | Azure AD tenant |
| `AZURE_CLIENT_ID` | Azure AD app registration client ID |
| `AZURE_CLIENT_SECRET` | Azure AD app registration secret |
| `JWT_SECRET_KEY` | Secret for signing application JWTs |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob storage connection |
| `REDIS_URL` | Redis connection for caching |

## Design System

This application uses the [Government of Alberta Design System](https://design.alberta.ca/) (`@abgov/web-components`). All UI components use `goa-` prefixed web components. The application meets WCAG 2.2 AA accessibility requirements including keyboard navigation, ARIA labels, color contrast, and focus management.

## License

Government of Alberta - Internal Use
