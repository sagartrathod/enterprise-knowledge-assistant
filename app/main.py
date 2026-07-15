from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import db_manager
from app.core.logger import logger
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle events, ensuring the asyncpg 
    database connection pool starts and terminates cleanly.
    """
    # 1. Startup phase
    try:
        await db_manager.connect_to_db()
        logger.info(f"Successfully booted {settings.APP_NAME} in [{settings.APP_ENV}] mode.")
    except Exception as e:
        logger.critical(f"Lifespan startup failure. Could not connect to database: {str(e)}")
        raise e
        
    yield
    
    # 2. Shutdown phase
    logger.info("Initiating application lifespan shutdown procedures...")
    await db_manager.close_db_connection()
    logger.info("Application lifespan shutdown completed safely.")


# Initialize the principal FastAPI application context
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Retrieval-Augmented Generation (RAG) Engine with raw SQL asyncpg & pgvector backend.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this configuration parameter to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the global unified API router layout under /api prefix[cite: 1]
app.include_router(api_router, prefix="/api")


@app.get("/health", status_code=status.HTTP_200_OK, tags=["System Health"])
async def health_check():
    """
    Simple verification probe endpoint used to monitor deployment status.
    """
    # Attempt to fetch the active pool to verify database connectivity status
    is_database_alive = False
    try:
        pool = db_manager.get_pool()
        async with pool.acquire() as conn:
            # Execute a fast dummy database transaction statement
            await conn.execute("SELECT 1;")
            is_database_alive = True
    except Exception as e:
        logger.error(f"Health check probe database connection failure: {str(e)}")

    return {
        "status": "healthy" if is_database_alive else "unhealthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database_connected": is_database_alive
    }