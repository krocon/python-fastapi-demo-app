import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.routers.rest_router import router as rest_router
from app.routers.proto_router import router as proto_router
from app.graphql.schema import graphql_router

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan Event: Initialisiert DB-Tabellen beim Start und schließt Verbindungen beim Stopp."""
    logger.info("🚀 Starte Backend-Dienste & synchronisiere Datenbank...")
    await init_db()
    yield
    logger.info("🛑 Fahre Backend-Dienste herunter...")
    await close_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS-Konfiguration für Frontend-Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. REST API Router einbinden
app.include_router(rest_router)

# 2. Protobuf API Router einbinden
app.include_router(proto_router)

# 3. Strawberry GraphQL Router einbinden (/graphql)
app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL"])


@app.get("/", tags=["Status"])
async def root_status():
    """Übersichts-Endpunkt mit Links zu allen 3 Schnittstellen."""
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "interfaces": {
            "rest": {
                "description": "REST API mit Swagger UI & OpenAPI Schemas",
                "docs": "http://127.0.0.1:8000/docs",
                "endpoints": {
                    "users": "/api/v1/users",
                    "items": "/api/v1/items",
                },
            },
            "graphql": {
                "description": "Strawberry GraphQL Explorer (GraphiQL)",
                "endpoint": "http://127.0.0.1:8000/graphql",
            },
            "protobuf": {
                "description": "Protocol Buffers Binär-Endpunkte (application/x-protobuf)",
                "endpoints": {
                    "create_user": "POST /api/v1/proto/users",
                    "list_users": "GET /api/v1/proto/users",
                    "get_user": "GET /api/v1/proto/users/{id}",
                },
            },
        },
    }
