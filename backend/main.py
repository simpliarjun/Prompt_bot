"""
FastAPI application entry point.

- Lifespan handler: connects MongoDB, creates indexes (correction #8).
- CORS middleware with parsed origins (correction #11).
- Correlation-ID middleware (correction #14).
- Includes all routers under /api prefix.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import close_db, connect_db, create_indexes, get_db
from logging_config import get_logger, setup_logging
from routers import auth, export, generate, grievances

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
setup_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: connect DB + create indexes. Shutdown: close DB."""
    logger.info("Starting CGMS backend…")
    await connect_db()
    await create_indexes()
    logger.info("CGMS backend ready")
    yield
    await close_db()
    logger.info("CGMS backend shut down")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="CGMS — Consumer Grievance Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS (correction #11)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Routers (all under /api)
# ---------------------------------------------------------------------------

app.include_router(auth.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(grievances.router, prefix="/api")
app.include_router(export.router, prefix="/api")


# ---------------------------------------------------------------------------
# Health endpoint (no auth)
# ---------------------------------------------------------------------------


@app.get("/api/health", tags=["health"])
async def health():
    """Health check — used by hosting platform probes."""
    try:
        db = get_db()
        await db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception:
        logger.error("Health check failed — database unreachable")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "disconnected"},
        )
