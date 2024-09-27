from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from models.session import Session
from database import get_db
from pydantic import BaseModel, EmailStr
import logging
import bcrypt
from schemas.login_Request import LoginRequest
from fastapi.security import OAuth2PasswordRequestForm
from services.jwt_handler import create_access_token
from services.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalars().first()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

        session_result = await db.execute(select(Session).where(Session.user_id == user.id))
        sessions = session_result.scalars().all()
        
        # Prepare session information
        session_info = [{"session_id": session.id} for session in sessions] if sessions else [{"message": "No sessions found"}]

        return {"message": "Login successful", 
                "access_token": access_token,
                "token_type": "bearer",##token type for OAuth
                "user_id": user.id, 
                "name": user.name, 
                "email": user.email, 
                "sessions": session_info}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
