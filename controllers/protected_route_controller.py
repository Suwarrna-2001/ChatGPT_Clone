from services.jwt_handler import get_current_user
from fastapi import APIRouter, Depends
from models.user import User

router = APIRouter()

@router.get("/protected-route")

async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Welcome to the protected route", "user": current_user.name}
