"""
FRS Data Management System - FastAPI Backend
Main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import BACKEND_HOST, BACKEND_PORT, CORS_ORIGINS, LOG_LEVEL, get_config_summary
from database import init_db
from routers.data_router import router as data_router
from routers.model_router import router as model_router
from services.llm_service import initialize_default_model

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FRS Data Management System",
    description="API for managing and comparing Formation Readiness State data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data_router)
app.include_router(model_router, prefix="/api", tags=["models"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup tasks"""
    try:
        logger.info("Starting FRS Data Management System...")
        
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize default LLM model
        initialize_default_model()
        
        # Log configuration summary
        config = get_config_summary()
        logger.info(f"Configuration: {config}")
        
        logger.info(f"Server ready at http://{BACKEND_HOST}:{BACKEND_PORT}")
    
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks on shutdown"""
    logger.info("Shutting down FRS Data Management System...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FRS Data Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
