from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import os

from db.database import get_db, init_db
from db.repositories import DatasetRepository, MetricsRepository
from schemas import DatasetCreate, Dataset, MetricsCreate, Metrics

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

# Initialize database
@app.on_event("startup")
def startup():
    init_db()
    # Create upload directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

# Dataset endpoints
@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Model Evaluation API is running"}

@app.get("/datasets/", response_model=List[Dataset])
def get_datasets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all datasets"""
    return DatasetRepository.get_datasets(db, skip=skip, limit=limit)

@app.get("/datasets/{dataset_id}", response_model=Dataset)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset by ID"""
    dataset = DatasetRepository.get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@app.post("/datasets/upload/", response_model=Dataset)
async def upload_dataset(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    format: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new dataset file"""
    dataset_create = DatasetCreate(name=name, description=description, format=format)
    return DatasetRepository.create_dataset(db, dataset_create, file)

@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset by ID"""
    success = DatasetRepository.delete_dataset(db, dataset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "ok", "message": f"Dataset {dataset_id} deleted"}

# Metrics endpoints
@app.post("/datasets/{dataset_id}/metrics/", response_model=Metrics)
def create_metrics(dataset_id: int, metrics: MetricsCreate, db: Session = Depends(get_db)):
    """Create metrics for a dataset"""
    # Ensure dataset_id in path matches dataset_id in body
    if metrics.dataset_id != dataset_id:
        raise HTTPException(status_code=400, detail="Dataset ID mismatch")
    
    return MetricsRepository.create_metrics(db, metrics)

@app.get("/datasets/{dataset_id}/metrics/", response_model=List[Metrics])
def get_dataset_metrics(dataset_id: int, db: Session = Depends(get_db)):
    """Get all metrics for a dataset"""
    dataset = DatasetRepository.get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return MetricsRepository.get_metrics_by_dataset(db, dataset_id)

@app.get("/metrics/{metrics_id}", response_model=Metrics)
def get_metrics(metrics_id: int, db: Session = Depends(get_db)):
    """Get metrics by ID"""
    metrics = MetricsRepository.get_metrics(db, metrics_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return metrics

@app.delete("/metrics/{metrics_id}")
def delete_metrics(metrics_id: int, db: Session = Depends(get_db)):
    """Delete metrics by ID"""
    success = MetricsRepository.delete_metrics(db, metrics_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return {"status": "ok", "message": f"Metrics {metrics_id} deleted"} 