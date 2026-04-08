from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.db.database import engine
from app.routes import api_router
from app.services.security_middleware import setup_security

from app.core.logging_setup import setup_logging, sentry_before_send

# Initialize secure logging
setup_logging()
logger = logging.getLogger(__name__)

# ── Sentry Observability ────────────────────────────
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    _ = sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.3,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
        environment=os.getenv("ENV", "development"),
        before_send=sentry_before_send,
    )
    logger.info("Sentry initialized for environment: %s", os.getenv("ENV", "development"))
else:
    logger.info("SENTRY_DSN not set — Sentry observability disabled.")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Setup resources
    from app.services.alert_engine import AlertEngine
    from app.services.token_refresh_service import TokenRefreshService
    
    alert_engine = AlertEngine()
    alert_engine.start()
    
    token_refresh = TokenRefreshService()
    token_refresh.start()
    
    yield
    # Cleanup resources
    await engine.dispose()

app = FastAPI(
    title="Dhyan API",
    description="Backend API for Dhyan Smart Trading Companion",
    version="1.0.0",
    lifespan=lifespan
)

# Apply global security (CORS, Rate Limiters, HSTS)
setup_security(app)

# Include the main API router
app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Dhyan API"}
