import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import setup_logging
from core.redis_client import ping as redis_ping
from modules.content.router import router as content_router
from modules.digest.router import router as digests_router
from modules.feedback.router import router as feedback_router
from modules.profile.router import router as profile_router
from modules.sources.router import router as sources_router

setup_logging()

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.debug else None,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    if settings.debug:
        # The scheduler runs in production; explicit CLI drives local dev.
        from modules.scheduler.jobs import start_scheduler

        start_scheduler()
    logging.getLogger("radar").info("Backend startup complete. Debug=%s", settings.debug)


@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {"status": "ok", "app": settings.app_name, "redis": await redis_ping()}


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(sources_router, prefix=settings.api_prefix)
app.include_router(content_router, prefix=settings.api_prefix)
app.include_router(digests_router, prefix=settings.api_prefix)
app.include_router(feedback_router, prefix=settings.api_prefix)
