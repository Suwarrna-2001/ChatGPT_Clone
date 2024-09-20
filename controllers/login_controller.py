from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from models.session import Session
from database import get_db
from pydantic import BaseModel, EmailStr
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from schemas.login_Request import LoginRequest

router = APIRouter()

@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalars().first()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Query the sessions related to the user
        session_result = await db.execute(select(Session).where(Session.user_id == user.id))
        sessions = session_result.scalars().all()
        
        # Prepare session information
        if sessions:
            session_info = [{"session_id": session.id} for session in sessions]
        else:
            session_info = [{"message": "No sessions found"}]


        return {"message": "Login successful", "user_id": user.id, "name": user.name, "email": user.email, "sessions": session_info}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
