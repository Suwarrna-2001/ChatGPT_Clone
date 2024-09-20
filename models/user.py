from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary Key
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # Relationship: One-to-Many with Session
    sessions = relationship("Session", back_populates="user")  
