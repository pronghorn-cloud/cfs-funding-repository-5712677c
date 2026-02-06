# CFS Funding Portal - Application Architecture

## Application Overview

| Property | Value |
|----------|-------|
| **Name** | CFS Funding Portal |
| **Version** | 0.1.0 |
| **Description** | Community Facilities and Supports - Shelter Funding Applications with integrated Social Vulnerability Index |
| **Repository** | https://github.com/pronghorn-cloud/cfs-funding-repository-5712677c.git |

---

## System Architecture Nodes

### Top-Level Nodes

```
[Frontend (Vue 3 SPA)] --HTTP/REST--> [Backend (FastAPI)] --async--> [PostgreSQL]
                                           |
                                           +--async--> [Azure Blob Storage]
                                           +--async--> [Redis]
                                           +--MSAL-->  [Azure AD]
                                           +--HTTP-->  [External Data Sources]
```

---

## Backend Nodes

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| DB Driver | asyncpg |
| Database | PostgreSQL |
| Migrations | Alembic |
| Auth | Azure AD (MSAL) + application-issued JWTs |
| Storage | Azure Blob Storage |
| Logging | structlog (JSON) |
| Monitoring | Prometheus metrics |
| PDF Generation | Jinja2 + WeasyPrint |
| Serialization | orjson |

### Entry Point

`app.main:app`

### Middleware Stack (outermost to innermost)

| Order | Node | Description |
|-------|------|-------------|
| 1 | `CorrelationIdMiddleware` | Adds X-Correlation-ID to all requests/responses |
| 2 | `RequestLoggingMiddleware` | Structured JSON logging of all requests |
| 3 | `RateLimitingMiddleware` | In-memory rate limiting per client IP |

### Module Nodes

#### auth
- **Description**: Azure AD MSAL authentication, JWT management, role-based access control
- **Models**: `User`, `UserSession`
- **Roles**: `applicant`, `reviewer`, `admin`
- **Dependencies**: `config`, `database`, `exceptions`
- **Connections**: Azure AD (MSAL), JWT secret key

#### organizations
- **Description**: CRUD for shelter organizations with soft delete and pagination
- **Models**: `Organization`
- **Dependencies**: `auth`, `database`, `common/pagination`

#### applications
- **Description**: Funding application lifecycle: create, edit sections, submit, review, decide
- **Models**: `FundingApplication`, `ApplicationSection`, `ApplicationStatusHistory`, `ApplicationComment`
- **Status Workflow**: `draft` -> `submitted` -> `under_review` -> `reviewed` -> `recommended` -> `approved` / `denied` / `withdrawn`
- **Dependencies**: `auth`, `database`, `organizations`

#### documents
- **Description**: File upload/download via Azure Blob Storage
- **Models**: `Document`
- **Dependencies**: `auth`, `database`, `applications`
- **Connections**: Azure Blob Storage (circuit breaker protected)

#### reviews
- **Description**: Reviewer scoring with weighted criteria and overall score calculation
- **Models**: `Review`, `ReviewScore`
- **Dependencies**: `auth`, `database`, `applications`

#### vulnerability
- **Description**: Social Vulnerability Index scoring engine, heatmap data, region comparison
- **Models**: `IndicatorCategory`, `Indicator`, `DataSource`, `IndicatorValue`, `SVIScore`
- **Submodules**:
  - `engine.py` - Pure computation (no DB): normalize, weight, composite, grade
  - `service.py` - DB orchestration and query layer
  - `catalog.py` - Indicator definitions
- **Dependencies**: `auth`, `database`, `geography`

#### ingestion
- **Description**: Data source ingestion pipeline with abstract adapter pattern
- **Models**: `IngestionJob`
- **Adapter Nodes**: `statscan`, `goa_health`, `environics`, `cfs_internal`, `scss`, `recovery_alberta`, `justice`
- **Dependencies**: `auth`, `database`, `vulnerability`
- **Connections**: External data source APIs (circuit breaker protected)

#### geography
- **Description**: Alberta regions and municipalities with GeoJSON boundaries
- **Models**: `Region`, `Municipality`
- **Dependencies**: `auth`, `database`

#### reporting
- **Description**: Briefing package generation (PDF via Jinja2 + WeasyPrint)
- **Templates**: `minister_briefing.html`, `treasury_board.html`
- **Dependencies**: `auth`, `database`, `applications`, `vulnerability`

#### notifications
- **Description**: Email service via Azure Communication Services (placeholder)
- **Connections**: Azure Communication Services (circuit breaker protected)

#### health
- **Description**: Kubernetes health probes: liveness, readiness, startup
- **Probes**: `/health/live`, `/health/ready`, `/health/startup`
- **Checks**: Database connectivity, Blob Storage connectivity

### Common/Shared Nodes

| Node | Description |
|------|-------------|
| `common/base_model.py` | TimestampMixin, SoftDeleteMixin, AuditMixin (UUID PKs) |
| `common/pagination.py` | PaginationParams, PaginatedResponse |
| `common/circuit_breaker.py` | 3-state circuit breaker (closed, open, half-open) |
| `common/metrics.py` | Prometheus counters/histograms |
| `common/audit.py` | AuditLog model and service |
| `common/logging_config.py` | structlog JSON configuration with BoundLogger |

---

## API Endpoint Nodes

### Infrastructure (no auth)

| Method | Path | Name | Description |
|--------|------|------|-------------|
| GET | `/` | root | Redirect to API docs |
| GET | `/health/live` | liveness | Liveness probe |
| GET | `/health/ready` | readiness | Readiness probe (checks DB, blob) |
| GET | `/health/startup` | startup | Startup probe |
| GET | `/api/docs` | swagger_ui | Swagger UI documentation |
| GET | `/metrics` | prometheus | Prometheus metrics endpoint |

### Auth (no auth required)

| Method | Path | Name | Description |
|--------|------|------|-------------|
| GET | `/api/v1/auth/login` | login | Initiate Azure AD login (redirects to dev-login in debug mode) |
| GET | `/api/v1/auth/dev-login` | dev_login | Dev-only: issue JWTs for mock user |
| GET | `/api/v1/auth/callback` | callback | Handle Azure AD OAuth callback |
| POST | `/api/v1/auth/refresh` | refresh | Refresh access token |
| POST | `/api/v1/auth/logout` | logout | Revoke refresh token |
| GET | `/api/v1/auth/me` | me | Get current user profile (auth: any) |

### Organizations (auth: any, delete: admin)

| Method | Path | Name |
|--------|------|------|
| POST | `/api/v1/organizations` | create_organization |
| GET | `/api/v1/organizations` | list_organizations |
| GET | `/api/v1/organizations/{org_id}` | get_organization |
| PATCH | `/api/v1/organizations/{org_id}` | update_organization |
| DELETE | `/api/v1/organizations/{org_id}` | delete_organization (admin) |

### Applications (auth: any, decision: admin)

| Method | Path | Name |
|--------|------|------|
| POST | `/api/v1/applications` | create_application |
| GET | `/api/v1/applications` | list_applications |
| GET | `/api/v1/applications/{app_id}` | get_application |
| PATCH | `/api/v1/applications/{app_id}` | update_application |
| POST | `/api/v1/applications/{app_id}/sections` | save_section |
| POST | `/api/v1/applications/{app_id}/status` | transition_status |
| POST | `/api/v1/applications/{app_id}/decision` | make_decision (admin) |
| POST | `/api/v1/applications/{app_id}/comments` | add_comment |
| GET | `/api/v1/applications/{app_id}/comments` | list_comments |

### Documents (auth: any)

| Method | Path | Name |
|--------|------|------|
| POST | `/api/v1/documents` | upload_document |
| GET | `/api/v1/documents/{doc_id}` | download_document |
| DELETE | `/api/v1/documents/{doc_id}` | delete_document |
| GET | `/api/v1/documents/application/{application_id}` | list_documents |

### Reviews (auth: reviewer/admin)

| Method | Path | Name |
|--------|------|------|
| POST | `/api/v1/reviews` | create_review |
| GET | `/api/v1/reviews/{review_id}` | get_review |
| PATCH | `/api/v1/reviews/{review_id}` | update_review |
| POST | `/api/v1/reviews/{review_id}/complete` | complete_review |
| GET | `/api/v1/reviews/application/{application_id}` | list_reviews_for_application |
| GET | `/api/v1/reviews/reviewer/me` | list_my_reviews |

### Reports (auth: admin)

| Method | Path | Name |
|--------|------|------|
| POST | `/api/v1/reports/generate` | generate_report |

### Vulnerability / SVI (auth: reviewer/admin, recalculate: admin)

| Method | Path | Name |
|--------|------|------|
| GET | `/api/v1/vulnerability/scores` | get_scores |
| GET | `/api/v1/vulnerability/heatmap` | get_heatmap |
| GET | `/api/v1/vulnerability/compare` | compare_regions |
| GET | `/api/v1/vulnerability/categories` | list_categories |
| GET | `/api/v1/vulnerability/indicators` | list_indicators |
| POST | `/api/v1/vulnerability/recalculate` | recalculate_scores (admin) |

### Ingestion (auth: admin)

| Method | Path | Name |
|--------|------|------|
| POST | `/api/v1/ingestion/trigger` | trigger_ingestion |
| GET | `/api/v1/ingestion/jobs/{job_id}` | get_job_status |
| GET | `/api/v1/ingestion/jobs` | list_jobs |

### Geography (auth: any)

| Method | Path | Name |
|--------|------|------|
| GET | `/api/v1/geography/regions` | list_regions |
| GET | `/api/v1/geography/regions/{region_id}` | get_region |
| GET | `/api/v1/geography/regions/{region_id}/geojson` | get_region_geojson |
| GET | `/api/v1/geography/geojson` | get_all_geojson |
| GET | `/api/v1/geography/municipalities` | list_municipalities |

---

## Frontend Nodes

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | TypeScript |
| Framework | Vue 3 |
| Build Tool | Vite 6 |
| State Management | Pinia |
| Routing | Vue Router 4 |
| Design System | @abgov/web-components (GoA Design System) |
| CSS | Tailwind CSS 3 |
| Maps | Leaflet (@vue-leaflet/vue-leaflet) |
| Charts | Chart.js (vue-chartjs) |
| HTTP Client | Axios |

### Entry Point

`src/main.ts` -> `App.vue` -> `<router-view>`

### Layout Nodes

| Layout | Used By | Description |
|--------|---------|-------------|
| `DefaultLayout.vue` | Most views | GoA App Header + Footer + main content slot |
| `AuthLayout.vue` | Login | Minimal centered layout |
| `AdminLayout.vue` | Admin views | GoA header + side menu + content |

### View/Route Nodes

#### Public (no auth)

| Path | Name | View | Layout |
|------|------|------|--------|
| `/` | landing | `LandingPage.vue` | DefaultLayout |
| `/login` | login | `LoginPage.vue` | AuthLayout |

#### Applicant (auth: any)

| Path | Name | View | Layout |
|------|------|------|--------|
| `/dashboard` | applicant-dashboard | `ApplicantDashboard.vue` | DefaultLayout |
| `/applications/new` | application-new | `ApplicationForm.vue` | DefaultLayout |
| `/applications/:id` | application-detail | `ApplicationDetail.vue` | DefaultLayout |

#### Reviewer (auth: reviewer/admin)

| Path | Name | View | Layout |
|------|------|------|--------|
| `/reviews` | reviewer-dashboard | `ReviewerDashboard.vue` | DefaultLayout |
| `/reviews/:appId` | application-review | `ApplicationReview.vue` | DefaultLayout |
| `/reviews/compare` | application-compare | `ApplicationCompare.vue` | DefaultLayout |

#### Vulnerability / SVI (auth: reviewer/admin)

| Path | Name | View | Layout |
|------|------|------|--------|
| `/vulnerability` | heatmap | `HeatmapView.vue` | DefaultLayout |
| `/vulnerability/compare` | region-comparison | `RegionComparison.vue` | DefaultLayout |
| `/vulnerability/indicators` | indicator-explorer | `IndicatorExplorer.vue` | DefaultLayout |
| `/vulnerability/data-sources` | data-source-status | `DataSourceStatus.vue` | DefaultLayout |

#### Admin (auth: admin)

| Path | Name | View | Layout |
|------|------|------|--------|
| `/reports` | report-generator | `ReportGenerator.vue` | DefaultLayout |
| `/admin` | admin-dashboard | `AdminDashboard.vue` | AdminLayout |
| `/admin/users` | user-management | `UserManagement.vue` | AdminLayout |
| `/admin/config` | system-config | `SystemConfig.vue` | AdminLayout |

### Store Nodes (Pinia)

| Store | Description | Connects To |
|-------|-------------|-------------|
| `auth` | JWT tokens, user profile, login/logout | auth.service -> `/api/v1/auth/*` |
| `applications` | Funding application CRUD and listing | applications.service -> `/api/v1/applications/*` |
| `organizations` | Organization CRUD and listing | organizations.service -> `/api/v1/organizations/*` |
| `reviews` | Review scoring and listing | reviews.service -> `/api/v1/reviews/*` |
| `vulnerability` | SVI scores, heatmap data, indicators | vulnerability.service -> `/api/v1/vulnerability/*` |
| `geography` | Regions, municipalities, GeoJSON | geography.service -> `/api/v1/geography/*` |
| `notifications` | Toast/notification UI state | (local only) |

### Service Nodes

| Service | API Base | Description |
|---------|----------|-------------|
| `api.ts` | `/api/v1` | Axios instance with JWT interceptor and auto-refresh on 401 |
| `auth.service.ts` | `/api/v1/auth` | Login, logout, refresh, profile |
| `applications.service.ts` | `/api/v1/applications` | Application CRUD, sections, status, comments |
| `organizations.service.ts` | `/api/v1/organizations` | Organization CRUD |
| `reviews.service.ts` | `/api/v1/reviews` | Review CRUD, scoring |
| `vulnerability.service.ts` | `/api/v1/vulnerability` | SVI scores, heatmap, indicators |
| `geography.service.ts` | `/api/v1/geography` | Regions, GeoJSON |
| `reports.service.ts` | `/api/v1/reports` | Report generation |

### Composable Nodes

| Composable | Description |
|------------|-------------|
| `useAuth` | Reactive auth state: user, isAuthenticated, isAdmin, isReviewer, login, logout |
| `usePagination` | Reusable pagination logic for list views |

---

## Database Nodes

### Engine

PostgreSQL 12+ | Database: `cfs_portal`

### Table Nodes

#### Identity Domain

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `users` | User accounts linked to Azure AD | -> `organizations` (FK) |
| `user_sessions` | JWT refresh token sessions | -> `users` (FK) |
| `audit_log` | System-wide audit trail | -> `users` (FK, nullable) |

#### Portal Domain

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `organizations` | Shelter organizations (soft delete) | <- `users`, <- `funding_applications` |
| `funding_applications` | Funding application records with status workflow | -> `organizations` (FK) |
| `application_sections` | Multi-step form section data (JSONB) | -> `funding_applications` (FK) |
| `application_status_history` | Status transition audit trail | -> `funding_applications` (FK) |
| `application_comments` | Internal and external comments | -> `funding_applications` (FK) |
| `documents` | Uploaded document metadata (files in Azure Blob) | -> `funding_applications` (FK) |
| `reviews` | Reviewer assessments of applications | -> `funding_applications` (FK) |
| `review_scores` | Individual scoring criteria per review | -> `reviews` (FK) |

#### SVI Domain

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `regions` | Alberta geographic regions with GeoJSON | <- `municipalities`, <- `indicator_values`, <- `svi_scores` |
| `municipalities` | Municipalities within regions | -> `regions` (FK) |
| `indicator_categories` | 6 SVI categories | <- `indicators` |
| `indicators` | Individual vulnerability indicators | -> `indicator_categories` (FK) |
| `data_sources` | External data source configurations | <- `indicator_values` |
| `indicator_values` | Raw and normalized values per region per year | -> `indicators` (FK), -> `regions` (FK), -> `data_sources` (FK) |
| `svi_scores` | Computed composite scores with KPMG grades | -> `regions` (FK) |
| `ingestion_jobs` | Data ingestion pipeline job tracking | (references data_source_id) |

### Seed Data

| Table | Count |
|-------|-------|
| regions | 24 |
| indicator_categories | 6 |
| indicators | 48 |
| data_sources | 7 |
| indicator_values | 2,736 |
| svi_scores | 57 |

### Migrations

| ID | Description |
|----|-------------|
| `001_initial_schema` | All tables, indexes, and foreign keys |
| `002_seed_svi_catalog` | Seed regions, categories, indicators, data sources |
| `003_seed_test_data` | Synthetic indicator values and pre-computed SVI scores |

---

## SVI Scoring Engine Node

### Computation Pipeline

```
Raw Indicator Values
  |
  v
[Normalize] -- min_max / z_score / percentile --> Normalized Values (0-100)
  |
  v
[Category Score] -- weighted average of indicators per category --> 6 Category Scores (0-100)
  |
  v
[Composite Score] -- weighted sum of category scores --> Single SVI Score (0-100)
  |
  v
[KPMG Grade] -- threshold mapping --> Grade (A/B/C/D/E)
  |
  v
[Risk Index] -- 0.4*VI + 0.2*Resources + 0.2*Pressure + 0.2*Funding --> Risk Score
```

### KPMG Grading Scale

| Grade | Range | Meaning |
|-------|-------|---------|
| A | 0-20 | Lowest vulnerability |
| B | 20-40 | Low vulnerability |
| C | 40-60 | Moderate vulnerability |
| D | 60-80 | High vulnerability |
| E | 80-100 | Highest vulnerability |

### SVI Categories (6)

1. Socioeconomic
2. Demographic
3. Health
4. Housing
5. Infrastructure
6. Environmental

### Data Source Adapters (7)

| Adapter | Source |
|---------|--------|
| `statscan` | Statistics Canada |
| `goa_health` | Government of Alberta Health |
| `environics` | Environics Analytics |
| `cfs_internal` | CFS Internal Data |
| `scss` | SCSS Data |
| `recovery_alberta` | Recovery Alberta |
| `justice` | Justice Data |

---

## Application Status Workflow Node

```
[draft] --> [submitted] --> [under_review] --> [reviewed] --> [recommended] --> [approved]
                                                                            \-> [denied]
[any state] --> [withdrawn]
```

---

## Security Nodes

| Node | Description |
|------|-------------|
| Azure AD (MSAL) | External identity provider |
| JWT Access Token | Short-lived (30 min), contains user claims |
| JWT Refresh Token | Long-lived (24 hr), stored as SHA-256 hash in DB |
| Role-Based Access | 3 roles: applicant, reviewer, admin |
| Rate Limiting | Per-IP, configurable per minute |
| CORS | Configurable allowed origins |
| Correlation IDs | UUID per request for distributed tracing |
| Audit Log | All mutations recorded with user, action, resource |
| Soft Deletes | Organizations, applications, documents |
| Circuit Breakers | On Azure Blob, external data source APIs, email service |

---

## Infrastructure Nodes

### Docker Compose Services

| Service | Image | Port |
|---------|-------|------|
| PostgreSQL | postgres:16-alpine | 5432 |
| Redis | redis:7-alpine | 6379 |
| Azurite | mcr.microsoft.com/azure-storage/azurite | 10000 |

### Health Probes

| Probe | Path | Checks |
|-------|------|--------|
| Liveness | `/health/live` | App process alive |
| Readiness | `/health/ready` | Database + Blob Storage |
| Startup | `/health/startup` | Initial DB migration applied |

### Monitoring

| Node | Endpoint/Feature |
|------|-----------------|
| Prometheus Metrics | `/metrics` |
| Structured Logging | JSON via structlog |
| Correlation IDs | X-Correlation-ID header |

---

## Accessibility

| Requirement | Standard |
|-------------|----------|
| Compliance | WCAG 2.2 AA |
| Design System | Government of Alberta Design System (@abgov/web-components) |
| Keyboard Navigation | Required |
| ARIA Labels | Required |
| Color Contrast | Required |
| Focus Management | Required |
