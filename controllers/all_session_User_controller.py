from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from models.session import Session  # Make sure to import your Session model
from database import get_db
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.get("/user/{user_id}/sessions")
async def get_user_sessions(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch the user to ensure they exist
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User with ID {user_id} not found.")
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch sessions related to the user
        sessions_result = await db.execute(select(Session).where(Session.user_id == user_id))
        sessions = sessions_result.scalars().all()

        if not sessions:
            return {"sessions": [], "message": "No sessions found"}

        return {"sessions": [{"session_id": session.id} for session in sessions]}

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
