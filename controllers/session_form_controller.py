import os
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from models.session import Session
from langchain_components.replier import prepare_prompt_and_chain, get_context
from database import get_db
import pdb
from typing import List, Dict, Union
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()


#create session for a particular id 
@router.post("/session")
async def create_session(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        user_id_str = body.get("user_id")
        user_id = int(user_id_str)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_session = Session(user_id=user_id)
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return {"message": "Session created successfully", "session_id": new_session.id}


    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")