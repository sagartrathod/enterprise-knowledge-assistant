from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from app.api.router import api_router
from app.core.config import settings
from app.core.database import db_manager
from app.core.logger import logger
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.request_context import RequestContextMiddleware


# ==============================================================================
# Application Lifespan
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    logger.info("=" * 100)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 100)

    try:

        await db_manager.connect_to_db()

        logger.info("Application   : %s", settings.APP_NAME)
        logger.info("Version       : %s", "1.0.0")
        logger.info("Environment   : %s", settings.APP_ENV)
        logger.info("Debug Mode    : %s", settings.DEBUG)

        logger.info("Database connected successfully.")

        logger.info("=" * 100)
        logger.info("REGISTERED ROUTES")
        logger.info("=" * 100)

        for route in app.routes:

            if isinstance(route, APIRoute):

                methods = ", ".join(
                    sorted(route.methods)
                )

                logger.info(
                    "%-15s %s",
                    methods,
                    route.path,
                )

        logger.info("=" * 100)
        logger.info("APPLICATION STARTED SUCCESSFULLY")
        logger.info("=" * 100)

    except Exception:

        logger.exception("Application startup failed.")

        raise

    yield

    logger.info("=" * 100)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 100)

    try:

        await db_manager.close_db_connection()

        logger.info(
            "Database connection pool closed successfully."
        )

    except Exception:

        logger.exception(
            "Failed while closing database connection."
        )

    logger.info("Application shutdown completed.")
    logger.info("=" * 100)


# ==============================================================================
# FastAPI Application
# ==============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Enterprise Retrieval-Augmented Generation (RAG) "
        "using FastAPI, PostgreSQL, pgvector, "
        "Hybrid Search, CrossEncoder Reranking and Groq."
    ),
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ==============================================================================
# Register Global Exception Handlers
# ==============================================================================

register_exception_handlers(app)

# ==============================================================================
# Middleware
# ==============================================================================

# Request Context Middleware
# (Request ID, Session ID, Start Time)
app.add_middleware(
    RequestContextMiddleware,
)

# Request / Response Logging
app.add_middleware(
    LoggingMiddleware,
)

# Cross Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# API Routes
# ==============================================================================

app.include_router(
    api_router,
    prefix="/api",
)

# ==============================================================================
# Root Endpoint
# ==============================================================================

@app.get(
    "/",
    tags=["System"],
)
async def root():

    logger.info("Root endpoint accessed.")

    return {
        "application": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# ==============================================================================
# Health Check
# ==============================================================================

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["System"],
)
async def health_check():

    logger.info("Health check requested.")

    database_connected = False

    try:

        pool = db_manager.get_pool()

        async with pool.acquire() as conn:

            await conn.fetchval("SELECT 1")

        database_connected = True

    except Exception:

        logger.exception(
            "Database health check failed."
        )

    logger.info(
        "Health Status | Database=%s",
        "Connected" if database_connected else "Disconnected",
    )

    return {
        "status": (
            "healthy"
            if database_connected
            else "unhealthy"
        ),
        "application": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "database_connected": database_connected,
    }