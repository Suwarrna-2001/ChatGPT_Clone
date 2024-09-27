from models.user import User
from schemas.register_user_req import RegisterUserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
import logging
from services.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from services.jwt_handler import create_access_token


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
        new_user.set_password(request.password)  
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": str(new_user.id)}, expires_delta=access_token_expires)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "name_of_user": new_user.name,
            "email_id": new_user.email,
            "access_token": access_token,  
            "token_type": "bearer"  # Indicate token type
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


###yha per simply database me user ke credentials store ho rhe hai lekin yha koi JWT involve nhi hoga 
# invole login me hoga lekin mai chahti hoon ki jaise hi user register kre vo login ho jaye aur aaram se 
# session me chat kre to mujhe yha jwt se token generate kerwana padega authentication ke liye. 