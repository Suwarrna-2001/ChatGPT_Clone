import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from database import get_db
from pydantic import BaseModel, EmailStr
from schemas.register_user_req import RegisterUserRequest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.post("/register-user")
async def register_user(request: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")
        new_user = User(name=request.name, email=request.email)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id, "name_of_user": new_user.name,"email_id": new_user.email}

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
