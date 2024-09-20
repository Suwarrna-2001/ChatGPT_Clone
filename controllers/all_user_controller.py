from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from database import get_db
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.get("/all-users-info")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    try:
        # Fetch all users from the database
        result = await db.execute(select(User))
        users = result.scalars().all()

        # Check if users list is empty
        if not users:
            logger.warning("No users found in the database.")
            return {"users": [], "message": "No users found"}

        # Manually serialize users to dictionary
        return {"users": [{"id": user.id, "name": user.name, "email": user.email} for user in users]}

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")