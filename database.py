from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Define the Base for ORM models
Base = declarative_base()

# Get the DATABASE_URL from the .env file
DATABASE_URL = os.getenv('DATABASE_URL')

# Create the async database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker with the async session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get the database session
async def get_db():
    async with async_session() as session:
        yield session
