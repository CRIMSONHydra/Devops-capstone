# Ecommerce Admin

Admin console for an online store: products, categories, customers, orders and a sales dashboard.

**Stack:** React + Vite (Nginx in prod) · FastAPI · SQLAlchemy + Alembic · PostgreSQL 16 · Pytest

## Run

```bash
cp .env.example .env
docker compose up --build        # UI: http://localhost:3000  API docs: http://localhost:8000/docs
```

## Develop / test

```bash
cd backend && uv sync                                  # creates .venv from uv.lock (Python 3.12)
cp .env.example .env                                  # DATABASE_URL=sqlite:///./dev.db (docker injects Postgres)
uv run pytest                                         # in-memory SQLite, never touches DATABASE_URL
TEST_DATABASE_URL=postgresql+psycopg2://... uv run pytest         # same tests against Postgres
uv run alembic upgrade head && uv run uvicorn app.main:app --reload   # dev DB: ./dev.db (SQLite)
uv run python -m app.seed                             # optional demo data
uv add <pkg>                                          # add a dependency (updates pyproject + uv.lock)
cd frontend && npm install && npm run dev             # proxies /api -> localhost:8000
```

## Kubernetes (minikube + Helm)

```bash
minikube start
minikube addons enable ingress                      # ingress-nginx, class "nginx"
kubectl apply -f k8s/namespace.yaml
helm upgrade --install ecommerce helm/ecommerce-admin -n ecommerce --set image.tag=<commit-sha>
kubectl get pods -n ecommerce
minikube tunnel                                     # then open http://127.0.0.1
```

Images come from GHCR (make the packages public), or use local ones:
`docker compose build`, then `minikube image load capstone-backend:latest` (same for frontend),
and deploy with:

```bash
helm upgrade --install ecommerce helm/ecommerce-admin -n ecommerce \
  --set image.tag=latest --set backend.image=capstone-backend --set frontend.image=capstone-frontend
```

## REST API

| Resource | Endpoints |
|---|---|
| `/api/categories` | GET, POST, GET/PUT/DELETE `/{id}` |
| `/api/products` | GET (search, category, low-stock, pagination), POST, GET/PUT/DELETE `/{id}` |
| `/api/customers` | GET, POST, GET/PUT/DELETE `/{id}` |
| `/api/orders` | GET, POST, GET/DELETE `/{id}`, PATCH `/{id}/status` |
| `/api/dashboard/stats` | GET |
| `/health`, `/metrics` | probes / Prometheus |

## Status

| Area | State |
|---|---|
| backend, frontend, docker-compose, tests | done |
| `.github/workflows/ci-cd.yml`, `k8s/`, `helm/`, `terraform/`, `monitoring/`, `scripts/` | scaffold only |
