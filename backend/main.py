"""
DockRadius — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.analyze import router as analyze_router

# ─── Logging Configuration ───────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dockradius")


# ─── Lifespan ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME}")
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set — LLM analysis will use fallback mode")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


# ─── App Instance ─────────────────────────────────────────────────

app = FastAPI(
    title="DockRadius API",
    description="DevOps visualization and risk analysis for Docker commands",
    version="1.0.0",
    lifespan=lifespan,
)


# ─── CORS ─────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ───────────────────────────────────────────────────────

app.include_router(analyze_router, tags=["Analysis"])


# ─── Health Check ─────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "DockRadius API"}
