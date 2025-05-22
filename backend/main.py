from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
from pydantic import BaseModel
import json
import os
import shutil
import uuid
import sys

# Database configuration
# Get current username - this should work on macOS and Linux
current_user = os.environ.get("USER", "vaseem")  # Default to 'vaseem' if USER env var not set
DATABASE_URL = f"postgresql://{current_user}@localhost:5432/ai_model_eval"
print(f"Connecting to PostgreSQL as user '{current_user}'")

# Create the engine without fallback to SQLite
engine = create_engine(DATABASE_URL)

# Test the connection to make sure it works
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"✅ Connected to PostgreSQL database as user '{current_user}'!")
except Exception as e:
    print(f"❌ Error connecting to PostgreSQL: {e}")
    print("Please ensure PostgreSQL is running and the database exists.")
    sys.exit(1)

# SQLAlchemy setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    format: str

class DatasetCreate(DatasetBase):
    pass

class DatasetModel(DatasetBase):
    id: int
    file_path: str
    size: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MetricsBase(BaseModel):
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    latency: Optional[List[float]] = None
    timestamps: Optional[List[str]] = None
    distribution: Optional[Dict[str, Any]] = None

class MetricsCreate(MetricsBase):
    dataset_id: int

class MetricsModel(MetricsBase):
    id: int
    dataset_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# SQLAlchemy models
class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    format = Column(String, nullable=False)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with metrics
    metrics = relationship("DatasetMetrics", back_populates="dataset", cascade="all, delete-orphan")

class DatasetMetrics(Base):
    __tablename__ = "dataset_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    model_name = Column(String, nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    latency = Column(JSON, nullable=True)  # Stored as JSON array
    timestamps = Column(JSON, nullable=True)  # Stored as JSON array
    distribution = Column(JSON, nullable=True)  # Stored as JSON object
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with dataset
    dataset = relationship("Dataset", back_populates="metrics")

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FastAPI app
app = FastAPI(title="AI Model Evaluation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# API endpoints
@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Model Evaluation API is running"}

@app.get("/datasets/", response_model=List[DatasetModel])
def get_datasets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all datasets"""
    return db.query(Dataset).offset(skip).limit(limit).all()

@app.get("/datasets/{dataset_id}", response_model=DatasetModel)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@app.post("/datasets/upload/", response_model=DatasetModel)
async def upload_dataset(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    format: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new dataset file"""
    # Create directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    import time
    timestamp = str(int(time.time() * 1000))
    file_path = os.path.join(upload_dir, f"{timestamp}_{file.filename}")
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create dataset in database
    db_dataset = Dataset(
        name=name,
        description=description,
        format=format,
        file_path=file_path,
        size=os.path.getsize(file_path)
    )
    
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    
    return db_dataset

@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete the file
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    
    # Delete from database
    db.delete(dataset)
    db.commit()
    
    return {"status": "ok", "message": f"Dataset {dataset_id} deleted"}

@app.post("/datasets/{dataset_id}/metrics/", response_model=MetricsModel)
def create_metrics(dataset_id: int, metrics: MetricsCreate, db: Session = Depends(get_db)):
    """Create metrics for a dataset"""
    # Ensure dataset_id in path matches dataset_id in body
    if metrics.dataset_id != dataset_id:
        raise HTTPException(status_code=400, detail="Dataset ID mismatch")
    
    # Check if dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == metrics.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Create metrics in database
    db_metrics = DatasetMetrics(
        dataset_id=metrics.dataset_id,
        model_name=metrics.model_name,
        accuracy=metrics.accuracy,
        precision=metrics.precision,
        recall=metrics.recall,
        f1_score=metrics.f1_score,
        latency=metrics.latency,
        timestamps=metrics.timestamps,
        distribution=metrics.distribution
    )
    
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    
    return db_metrics

@app.get("/datasets/{dataset_id}/metrics/", response_model=List[MetricsModel])
def get_dataset_metrics(dataset_id: int, db: Session = Depends(get_db)):
    """Get all metrics for a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return db.query(DatasetMetrics).filter(DatasetMetrics.dataset_id == dataset_id).all()

@app.get("/metrics/{metrics_id}", response_model=MetricsModel)
def get_metrics(metrics_id: int, db: Session = Depends(get_db)):
    """Get metrics by ID"""
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
    if metrics is None:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return metrics

@app.delete("/metrics/{metrics_id}")
def delete_metrics(metrics_id: int, db: Session = Depends(get_db)):
    """Delete metrics by ID"""
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    # Delete from database
    db.delete(metrics)
    db.commit()
    
    return {"status": "ok", "message": f"Metrics {metrics_id} deleted"}


