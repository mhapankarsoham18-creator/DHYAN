from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

from .auth import router as auth_router
from .portfolio import router as portfolio_router
from .markets import router as markets_router
from .orders import router as orders_router
from .alerts import router as alerts_router
from .billing import router as billing_router
from .webhooks import router as webhooks_router
from .notifications import router as notifications_router
from .ai import router as ai_router
from app.services.price_relay import router as websocket_router

api_router.include_router(auth_router)
api_router.include_router(portfolio_router)
api_router.include_router(markets_router)
api_router.include_router(orders_router)
api_router.include_router(alerts_router)
api_router.include_router(billing_router)
api_router.include_router(webhooks_router)
api_router.include_router(notifications_router)
api_router.include_router(ai_router)
api_router.include_router(websocket_router)
