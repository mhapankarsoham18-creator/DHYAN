from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import os
import logging

logger = logging.getLogger(__name__)

# Phase 4.2: Rate Limiting
limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv("REDIS_URL", "memory://"))

def setup_security(app: FastAPI):
    # Register limiting metadata for slowapi
    app.state.limiter = limiter
    
    # Phase 4.5: CORS Configuration (Strict Whitelist)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://dhyan.app",
            "https://staging.dhyan.app",
            # No wildcards allowed for production
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Phase 4.6: Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    # Force HTTPS in production
    if os.getenv("ENV") == "production":
        app.add_middleware(HTTPSRedirectMiddleware)

    # Custom handler for rate limiting
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."},
        )

    logger.info("Backend security middlewares (CORS, Headers, Rate Limiting) configured.")
