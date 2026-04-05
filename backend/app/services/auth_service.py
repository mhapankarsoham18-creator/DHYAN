import os
import sys
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models import User

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    print("FATAL: JWT_SECRET environment variable is missing", file=sys.stderr)
    sys.exit(1)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        # Guarantee JWT_SECRET is treated as string for the decrypter
        secret: str = str(JWT_SECRET)
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
        user_id_val = payload.get("sub")
        if user_id_val is None:
            raise credentials_exception()
        user_id = str(user_id_val)
    except jwt.PyJWTError:
        raise credentials_exception()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception()
    return user
