import time
import logging
from functools import wraps
from fastapi import Request, HTTPException
from app.core.redis import get_upstash_redis

logger = logging.getLogger(__name__)

def upstash_rate_limit(max_requests: int, window_seconds: int):
    """
    A persistent rate limiter using Upstash Redis REST API.
    If Redis is unreachable, it fails open (allows traffic).
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            # Extract request from args if not in kwargs (FastAPI injects it if annotated)
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                # If we cannot find the request object, we cannot rate limit by IP.
                return await func(*args, **kwargs)

            client = await get_upstash_redis()
            if not client:
                # Fail open if Upstash is not configured
                return await func(*args, **kwargs)

            # Get client IP
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0]
            else:
                ip = request.client.host if request.client else "unknown"

            route = request.url.path
            # Sliding window approach simplified: current epoch window
            window_id = int(time.time() / window_seconds)
            key = f"rate_limit:{ip}:{route}:{window_id}"

            try:
                # Increment the counter
                count = await client.incr(key)
                if count == 1:
                    # Set expiry on first increment
                    await client.expire(key, window_seconds)
                
                if count > max_requests:
                    logger.warning(f"Rate limit exceeded for IP {ip} on route {route}")
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests. Please try again later."
                    )
            except HTTPException:
                raise
            except Exception as e:
                # Fail open on Redis errors
                logger.error(f"Rate limiting Upstash error: {e}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
