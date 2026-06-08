# Personal Finance System

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-A30000?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-2.13-22B5BF?style=for-the-badge&logo=recharts&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.31-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.27-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-23-499848?style=for-the-badge&logo=gunicorn&logoColor=white)

Full-stack personal finance manager with dual-database architecture (PostgreSQL + MongoDB), automated transaction categorization, budget alerts, credit card tracking, cash flow projections, and investment portfolio management.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL   │
│  React/Vite  │     │  Django/DRF  │     │  (Structured) │
│  Tailwind    │     │  Gunicorn    │     │  Users/Budgets│
│  Recharts    │     │  Celery      │     │  Goals/Cards  │
└──────────────┘     │              │     └──────────────┘
       │             │              │     ┌──────────────┐
       │             │              │────▶│   MongoDB     │
       │             │              │     │ (Unstructured)│
       │             │              │     │ Transactions  │
       │             └──────────────┘     │ Audit Trails  │
       │                                  └──────────────┘
       │             ┌──────────────┐
       └────────────▶│    Nginx     │
                     │  (Reverse    │
                     │   Proxy)     │
                     └──────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript 5.6, Vite 6, Tailwind CSS 3.4, Recharts 2.13 |
| **Backend** | Python 3.11+, Django 5.1, Django REST Framework 3.15, Celery 5.4 |
| **Databases** | PostgreSQL 16 (relational), MongoDB 7 (documents) |
| **Infra** | Docker, Kubernetes 1.31, Nginx 1.27, Gunicorn, Redis 7 |

## Features

### Transaction Management
- Manual transaction CRUD (MongoDB-backed)
- **OFX/QFX and CSV file upload** with automatic parsing
- **Auto-categorization** via regex rules (e.g., "Uber" → Transport)
- Background Celery task for batch categorization
- Recurring transactions with future execution dates

### Budgets & Alerts
- Monthly category budgets with spend tracking
- **Automatic alerts** at 80% and 100% of budget limit
- Budget-per-category, month, and year

### Credit Cards
- Card registration with closing/due days
- Statement tracking with installment projection
- Payment status management

### Cash Flow Projection
- `/api/cash-flow/` endpoint: `Current Balance + Predicted Income - Scheduled Expenses`
- Daily projections for 30/60/90 days

### Financial Goals
- Savings buckets with target/current amounts
- Real-time progress percentage
- Visual progress bars on dashboard

### Investment Portfolio
- Track fixed income, stocks, crypto, real estate
- Automatic P&L calculation (total invested, current value, return %)

### Dashboard
- Net Worth Evolution (line chart)
- Category Expenses (pie chart)
- Income vs Expenses (bar chart)
- Goal progress and upcoming recurring transactions

### Theme Persistence
- Light/Dark mode toggle
- Preference saved to PostgreSQL via `PATCH /api/profile/theme/`
- Automatically applied on login (not LocalStorage-only)

## Project Structure

```
personal-finance-system/
├── backend/
│   ├── core/               # Django settings, URLs, WSGI, Celery
│   ├── apps/
│   │   ├── users/          # Auth, profile, theme preference
│   │   ├── finance/        # Budgets, cards, goals, investments
│   │   └── transactions/   # MongoDB models, parsers, upload, categorization
│   ├── mongodb_utils/      # PyMongo client
│   ├── tests/              # Transaction + Budget integration tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Dashboard, ThemeToggle, Charts, Layout
│   │   ├── context/        # AuthContext, ThemeContext
│   │   └── services/       # Typed API client
│   ├── tests/              # Vitest + RTL tests
│   ├── Dockerfile
│   └── nginx.conf
├── k8s/                    # Kubernetes manifests with probes
├── scripts/                # Smoke tests & deployment verification
└── docker-compose.yml
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Running with Docker

```bash
git clone <repo-url>
cd personal-finance-system

# Start all services
docker compose up --build

# Backend:   http://localhost:8000
# Frontend:  http://localhost:3000
# API docs:  http://localhost:8000/api/schema/swagger-ui/
```

### Local Development

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit as needed
python manage.py migrate
python manage.py runserver
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev   # proxies /api to localhost:8000
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login/` | Login with username/password |
| POST | `/api/auth/logout/` | Logout |
| GET/PATCH | `/api/profile/` | Get/update user profile |
| PATCH | `/api/profile/theme/` | Update theme preference |
| GET/POST | `/api/transactions/` | List/create transactions |
| GET/PUT/DELETE | `/api/transactions/:id/` | Transaction detail |
| POST | `/api/transactions/upload/` | Upload OFX/CSV file |
| GET | `/api/budgets/` | List budgets |
| POST | `/api/budgets/` | Create budget |
| GET | `/api/cash-flow/` | Cash flow projection (30/60/90 days) |
| GET | `/api/dashboard/` | Aggregated dashboard data |
| GET | `/api/health/` | Health check (PostgreSQL + MongoDB) |

## Testing

```bash
# Backend
cd backend && python manage.py test

# Frontend
cd frontend && npm test
```

## Deployment Verification

The CI/CD pipeline includes automated smoke tests:

```bash
# Run smoke tests against any environment
FRONTEND_URL=https://staging.example.com \
BACKEND_URL=https://staging.example.com/api \
bash scripts/smoke-test.sh

# Full K8s verification with rollback on failure
NAMESPACE=production DEPLOYMENT_NAME=backend \
bash scripts/deploy-verify.sh
```

Smoke tests verify:
1. Frontend returns HTTP 200
2. Backend `/api/health/` confirms PostgreSQL + MongoDB connectivity
3. Login API returns user profile
4. Dashboard API returns aggregated data

## Kubernetes

Deploy to K8s cluster:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

All deployments include `livenessProbe` and `readinessProbe` referencing `/api/health/` to prevent traffic hitting unhealthy instances.
