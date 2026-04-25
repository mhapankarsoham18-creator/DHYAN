import sys
import os
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

from typing import Any
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.db.database import get_db
from app.models import User, BrokerConnection
from app.services.auth_service import create_access_token, get_current_user
from app.core.upstash_rate_limiter import upstash_rate_limit

# Setup Firebase Admin
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase_adminsdk.json")
if not os.path.exists(firebase_cred_path):
    print(f"WARNING: Firebase Admin credentials not found at {firebase_cred_path}", file=sys.stderr)
else:
    try:
        cred = credentials.Certificate(firebase_cred_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase Admin: {e}", file=sys.stderr)

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenExchangeRequest(BaseModel):
    token: str = Field(..., max_length=2000)
    phone_number: str = Field(..., max_length=20)

class TokenExchangeResponse(BaseModel):
    token: str
    user: dict[str, Any]

class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=20)

@router.post("/exchange-token", response_model=TokenExchangeResponse)
@upstash_rate_limit(max_requests=5, window_seconds=900)
async def exchange_token(request: Request, req: TokenExchangeRequest, db: AsyncSession = Depends(get_db)):
    # Verify the Firebase token
    if not firebase_admin._apps:
        # In strict production, this would fail. For now, we enforce it but allow graceful degradation if permitted.
        raise HTTPException(status_code=500, detail="Firebase Admin not initialized on backend.")
    
    # 1. Device Attestation (App Check)
    app_check_token = request.headers.get("X-Firebase-AppCheck", "")
    if not app_check_token:
        # Strict enforcement: Fail if it's missing (prevent non-app abuse)
        raise HTTPException(status_code=401, detail="Unauthorized: AppCheck missing.")
    
    try:
        from firebase_admin import app_check
        app_check.verify_token(app_check_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: AppCheck invalid. {e}")

    # 2. Identity Verification
    try:
        decoded_token = firebase_auth.verify_id_token(req.token)
        phone = decoded_token.get("phone_number")
        if not phone or phone != req.phone_number:
            raise HTTPException(status_code=401, detail="Phone number mismatch or missing in token.")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase Token: {str(e)}")
    
    result = await db.execute(select(User).where(User.phone_number == req.phone_number))
    user = result.scalars().first()
    
    if not user:
        # Create a new user if it doesn't exist
        user = User(
            phone_number=req.phone_number,
            name="New User",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    # Get active broker connections
    broker_result = await db.execute(select(BrokerConnection).where(BrokerConnection.user_id == user.id, BrokerConnection.is_active == True))
    connected_brokers = [b.broker_name for b in broker_result.scalars().all()]
    
    # Generate internal JWT
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenExchangeResponse(
        token=access_token,
        user={
            "id": str(user.id),
            "phone_number": user.phone_number,
            "name": user.name,
            "simulation_active": user.simulation_active,
            "virtual_balance": user.virtual_balance,
            "connected_brokers": connected_brokers,
            "preferences": {"theme": "dark", "simple_mode": True}
        }
    )

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    broker_result = await db.execute(select(BrokerConnection).where(BrokerConnection.user_id == current_user.id, BrokerConnection.is_active == True))
    connected_brokers = [b.broker_name for b in broker_result.scalars().all()]

    return {
        "id": str(current_user.id),
        "phone_number": current_user.phone_number,
        "name": current_user.name,
        "simulation_active": current_user.simulation_active,
        "virtual_balance": current_user.virtual_balance,
        "connected_brokers": connected_brokers,
        "preferences": {"theme": "dark", "simple_mode": True}
    }

@router.patch("/profile")
async def update_profile(req: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if req.name is not None:
        current_user.name = req.name
    if req.phone_number is not None:
        current_user.phone_number = req.phone_number
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return {"message": "Profile updated", "user": {"id": str(current_user.id), "name": current_user.name, "phone_number": current_user.phone_number}}

@router.post("/simulation/start")
async def start_simulation(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Start 7-day simulation with 2,50,000 balance
    current_user.simulation_active = True
    current_user.simulation_start_date = datetime.now(timezone.utc)
    current_user.virtual_balance = 250000.0
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "message": "Simulation started for 7 days",
        "simulation_active": current_user.simulation_active,
        "virtual_balance": current_user.virtual_balance
    }
