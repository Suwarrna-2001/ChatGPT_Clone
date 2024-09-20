from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List

class LoginRequest(BaseModel):
    email: EmailStr