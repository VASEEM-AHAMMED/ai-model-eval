from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL credentials from the environment variables
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Construct the DATABASE_URL from these credentials
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create sessionmaker for async session handling
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Function to create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created!")


# Function to start the app and create tables
async def start_app():
    await create_tables()

from backend.database import SessionLocal

# Helper function to get the database session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

