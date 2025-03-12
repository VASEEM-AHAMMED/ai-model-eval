from fastapi import FastAPI, File, UploadFile, Depends
from backend.database import SessionLocal  # Import async database connection object and SessionLocal
from backend.evaluation import router as evaluation_router
import os
from pathlib import Path
from dotenv import load_dotenv
from backend.models import ModelMetadata  # Import your model metadata model
import shutil
import uuid
from sqlalchemy.orm import Session
from backend.database import get_db 

# Load environment variables from .env
load_dotenv()

app = FastAPI()

MODEL_STORAGE_DIR = Path("models")
MODEL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.include_router(evaluation_router, prefix="/evaluation", tags=["evaluation"])

# Connect to the database on startup
@app.on_event("startup")
async def startup():
    try:
        # Database connection logic (with asyncpg or SQLAlchemy)
        DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
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
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        query = "SELECT version();"  # Simple query to check the PostgreSQL version
        result = db.execute(query).fetchone()  # Fetch the result
        return {"db_version": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Model Evaluation Platform!"}

# Model Upload API
@app.post("/upload-model/")
async def upload_model(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Generate a unique ID for the model
        model_id = str(uuid.uuid4())
        
        # Save the model file to the file system
        file_location = MODEL_STORAGE_DIR / file.filename
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save model details to the database asynchronously
        model_metadata = ModelMetadata(name=file.filename, accuracy=None, loss=None)
        db.add(model_metadata)
        db.commit()
        db.refresh(model_metadata)  # Retrieve the inserted row with the ID
        
        return {"filename": file.filename, "model_id": model_metadata.id, "message": "Model uploaded successfully!"}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

