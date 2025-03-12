from fastapi import FastAPI, File, UploadFile
from backend.database import database  # Import async database connection object
from databases import Database
import asyncpg  # For PostgreSQL support
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()

MODEL_STORAGE_DIR = Path("models")
MODEL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Connect to the database on startup
@app.on_event("startup")
async def startup():
    try:
        DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        database = Database(DATABASE_URL)  # Pass DATABASE_URL to the database connection
        await database.connect()  # Connect to the PostgreSQL database asynchronously
        print("Connected to the database.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

# Disconnect from the database on shutdown
@app.on_event("shutdown")
async def shutdown():
    try:
        await database.disconnect()  # Disconnect asynchronously
        print("Disconnected from the database.")
    except Exception as e:
        print(f"Error disconnecting from the database: {e}")

# Example endpoint to test DB connection
@app.get("/db_test")
async def test_db_connection():
    try:
        query = "SELECT version();"  # Simple query to check the PostgreSQL version
        result = await database.fetch_one(query)  # Fetch the result asynchronously
        return {"db_version": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Model Evaluation Platform!"}

# Model Upload API
@app.post("/upload-model/")
async def upload_model(file: UploadFile = File(...)):
    file_location = MODEL_STORAGE_DIR / file.filename
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "message": "Model uploaded successfully!"}
