import os
from upstash_redis.asyncio import Redis as AsyncUpstashRedis
import logging

logger = logging.getLogger(__name__)

# Initialize Upstash Redis if credentials are provided
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

upstash_redis = None

if UPSTASH_URL and UPSTASH_TOKEN:
    try:
        upstash_redis = AsyncUpstashRedis(url=UPSTASH_URL, token=UPSTASH_TOKEN)
        logger.info("Upstash Redis configured successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Upstash Redis: {e}")
else:
    logger.warning("Upstash Redis credentials not found in environment. Fallbacks will be used.")

async def get_upstash_redis() -> AsyncUpstashRedis | None:
    return upstash_redis
