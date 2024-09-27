import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from database import get_db
from jwt import PyJWTError
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

SECRET_KEY = "hmBnDrwonGh6Hp9FkZIYD4kuHr8P1PdA83_qcAYg5rI"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")#yha se token retrieve hoga 

def create_access_token(data: dict, expires_delta: timedelta = None):#JWT token created
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):#verifcation
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    return user

###header, payload, signature