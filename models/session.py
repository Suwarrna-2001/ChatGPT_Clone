from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)  
    user_id = Column(Integer, ForeignKey('users.id'))  

    # Relationship: Many-to-One with User
    user = relationship("User", back_populates="sessions")  # Each Session belongs to one User
