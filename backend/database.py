import os
import asyncio
from databases import Database
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Base

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
# Create the database object for async interaction
database = Database(DATABASE_URL)

# Create async engine and session for the models
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Async function to create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# This will run the table creation in the background when the app starts
async def start_app():
    await create_tables()

# This function can be called from your FastAPI app initialization (in main.py)
loop = asyncio.get_event_loop()
loop.create_task(start_app())
