from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.session import Session
from database import get_db
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.get("/all-sessions")
async def get_all_sessions(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Session))
        sessions = result.scalars().all()

        if not sessions:
            logger.warning("No sessions found in the database.")
            return {"sessions": [], "message": "No sessions found"}

        return {
            "sessions": [
                {
                    "id": session.id,
                    "user_id": session.user_id
                }
                for session in sessions
            ]
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")