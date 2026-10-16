from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .routers import categories, customers, dashboard, orders, products

app = FastAPI(title="Ecommerce Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator(excluded_handlers=["/metrics", "/health", "/api/health"]).instrument(app).expose(
    app, include_in_schema=False
)

for r in (categories, products, customers, orders, dashboard):
    app.include_router(r.router)


@app.get("/health", tags=["health"])
@app.get("/api/health", tags=["health"], include_in_schema=False)
def health():
    return {"status": "ok"}
