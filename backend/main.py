from fastapi import FastAPI, File, UploadFile, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
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
from backend.database import create_tables
from sqlalchemy import text
from dataset_manager import DatasetManager
from backend.models import Dataset  # Import your dataset model

# Load environment variables from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_STORAGE_DIR = Path("models")
MODEL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.include_router(evaluation_router, prefix="/evaluation", tags=["evaluation"])

# Connect to the database on startup

@app.on_event("startup")
async def startup():
    try:
        DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD.replace('@', '%40')}@{DB_HOST}:{DB_PORT}/{DB_NAME}"   
        # Get the DB session asynchronously
        async with SessionLocal() as db:
            # Test database connection
            query = text("SELECT 1;")  # Wrap query in text()
            result = await db.execute(query)  # Use await for async execution
            row = result.fetchone()  # Fetch result
            if row:
                print("Database is reachable.")
            else:
                print("Database did not respond as expected.")
        
        # Ensure tables are created
        await create_tables()
        print("Tables created successfully.")
        
    except Exception as e:
        print(f"Error during startup: {e}")





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
        await db.commit()  # Await the commit
        await db.refresh(model_metadata)  # Await the refresh
        
        return {"filename": file.filename, "model_id": model_metadata.id, "message": "Model uploaded successfully!"}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

dataset_manager = DatasetManager()

# Dataset management endpoints
@app.post("/datasets/")
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None)
):
    try:
        dataset = await dataset_manager.create_dataset(
            file=file,
            name=name,
            description=description
        )
        return {"message": "Dataset uploaded successfully", "dataset": dataset}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: int):
    dataset = await dataset_manager.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@app.post("/datasets/{dataset_id}/metrics")
async def save_dataset_metrics(
    dataset_id: int,
    model_name: str,
    metrics: Dict[str, Any]
):
    try:
        metrics = await dataset_manager.save_metrics(
            dataset_id=dataset_id,
            model_name=model_name,
            metrics=metrics
        )
        return {"message": "Metrics saved successfully", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/datasets/{dataset_id}/metrics")
async def get_dataset_metrics(dataset_id: int):
    metrics = await dataset_manager.get_dataset_metrics(dataset_id)
    return metrics

@app.get("/datasets/")
async def list_datasets():
    db = SessionLocal()
    try:
        datasets = db.query(Dataset).all()
        return datasets
    finally:
        db.close()


