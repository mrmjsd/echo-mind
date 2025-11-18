from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# from app.core.config import settings
from api.routes import router as audio_router
from core.logging_config import get_logger, setup_logging
import os

# Configure logging once at startup
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Speech-to-Text API",
    description="API for transcribing speech to text",
    version="1.0.0"
)

# CORS middleware
# Explicitly allow common Streamlit origins and support env override.
# Note: When allow_credentials=True, FastAPI cannot use wildcard "*" for origins.
default_origins = [
    "http://0.0.0.0:6000",
    "http://127.0.0.1:6000",
    "http://0.0.0.0:8501",
    "http://127.0.0.1:8501",
]
env_origins = os.getenv("ALLOWED_ORIGINS")
allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()] if env_origins else default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audio_router, prefix="/api/v1", tags=["audio"])
logger.info("Routers registered under /api/v1")

if __name__ == "__main__":
    logger.info("Starting uvicorn server on 0.0.0.0:3030")
    uvicorn.run("app.main:app", host="0.0.0.0", port=3030, reload=True)