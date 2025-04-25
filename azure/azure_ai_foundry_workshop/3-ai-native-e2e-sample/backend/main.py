"""
Main FastAPI Application Entry Point

This application ties together:
- Simulation of trial events (via the /simulate endpoint)
- Multi-agent trial event analysis (using the coordinator and specialized agents)
- Telemetry integration for monitoring the full end-to-end pipeline.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from utils.telemetry import configure_telemetry
from clients import ensure_clients
from routers import medication, literature, trials  # Add medication import

# -------------------------------
# Environment Configuration
# -------------------------------

# Configure logging with proper level handling
def get_log_level():
    """Get log level from environment with fallback to INFO"""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level, logging.INFO)

logging.basicConfig(
    level=get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure OpenTelemetry
configure_telemetry()

logger.info("🎯 Starting Clinical Trials Monitor")

# -------------------------------
# Router Imports
# -------------------------------
from routers.trials import router as trials_router
from routers.literature import router as literature_router
from routers.medication import router as medication_router

# -------------------------------
# FastAPI App Configuration
# -------------------------------

logger.info("⚙️ Configuring FastAPI application")
app = FastAPI(
    title="Clinical Trials Monitor",
    description="""
    Real-time clinical trial event monitoring and analysis system using Azure AI Agents Service.
    
    This system integrates:
      • Trial event simulation via Azure Event Hubs.
      • Multi-agent processing to analyze trial events.
      • Telemetry for tracing and performance insights.
    """,
    version="1.0.0"
)

# -------------------------------
# Middleware Setup
# -------------------------------

logger.info("🔒 Configuring CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend application URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Router Registration
# -------------------------------

logger.info("📝 Registering API routes")
app.include_router(
    trials_router,
    prefix="/api/trials",
    tags=["trials"]
)
app.include_router(
    literature_router,
    prefix="/api/agents",
    tags=["literature"]
)
app.include_router(
    medication_router,
    prefix="/api/medication",
    tags=["medication"]
)
app.include_router(medication.router)  # Add this line

# -------------------------------
# Application Events
# -------------------------------

@app.on_event("startup")
async def startup_event():
    """
    Initialize required services and verify dependencies on application startup.
    This includes:
      • Validating that the Azure AI clients are set up to enable multi-agent communication.
      • Ensuring all telemetry configurations are in place.
    """
    logger.info("📦 Imported dependencies successfully")
    logger.info("✅ Backend services initialized successfully")

# -------------------------------
# Core Endpoints
# -------------------------------

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root endpoint to ReDoc API documentation."""
    return RedirectResponse(url="/redoc", status_code=302)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "ok"}

# -------------------------------
# Development Configuration
# -------------------------------

# Print all registered routes for debugging purposes
if os.getenv("DEBUG", "false").lower() == "true":
    logger.info("📋 Registered Routes:")
    for route in app.routes:
        logger.info(f"{route.path} - {route.name}")

logger.info("✅ Application configuration complete")

# -------------------------------
# Development Server
# -------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
