import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from db.config import DATABASE_URL

# Create SQLAlchemy engine with proper error handling
def create_db_engine():
    """Create and return a database engine with error handling"""
    try:
        # Try to connect to PostgreSQL first
        engine = create_engine(DATABASE_URL)
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        print(f"✅ Connected to PostgreSQL database!")
        return engine
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        
        # Check if we should fallback to SQLite or exit
        if os.environ.get("FORCE_POSTGRES", "").lower() == "true":
            print("FORCE_POSTGRES is enabled. Exiting application.")
            sys.exit(1)
        
        print("Falling back to SQLite database")
        sqlite_url = "sqlite:///./ai_model_eval.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

# Create engine
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize database
def init_db():
    Base.metadata.create_all(bind=engine) 