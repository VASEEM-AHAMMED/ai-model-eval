from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Query, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import os
import shutil
import time

# Import database components
from db.database import get_db, init_db
from db.models import Dataset, DatasetMetrics
from db.schemas import (
    DatasetCreate, DatasetRead, DatasetUpdate,
    MetricsCreate, MetricsRead, MetricsUpdate
)

# Import new modules
import search
import exporters
import visualization
import auth
import batch

# Initialize FastAPI app
app = FastAPI(
    title="AI Model Evaluation API",
    description="API for evaluating AI model performance on various datasets",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# Initialize database
init_db()

# API endpoints
@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Model Evaluation API is running"}

# Authentication endpoints
@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(auth.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=auth.User)
async def read_users_me(current_user: auth.User = Depends(auth.get_current_active_user)):
    return current_user

# Dataset endpoints
@app.get("/datasets/", response_model=List[DatasetRead])
def get_datasets(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all datasets"""
    return db.query(Dataset).offset(skip).limit(limit).all()

@app.post("/datasets/search", response_model=List[DatasetRead])
def search_datasets(
    query: Optional[str] = None,
    format: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search datasets with filters and sorting"""
    filters = {}
    if format:
        filters["format"] = format
    if min_size:
        filters["min_size"] = min_size
    if max_size:
        filters["max_size"] = max_size
        
    return search.search_datasets(
        db,
        query=query,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
        **filters
    )

@app.get("/datasets/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@app.post("/datasets/upload/", response_model=DatasetRead)
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
    
    # Read file content for validation
    content = await file.read()
    
    # For CSV files, attempt auto-fixing and validate
    if format.lower() == 'csv':
        # Try to fix common CSV formatting issues
        fixed_content, was_fixed = exporters.fix_csv_formatting(content)
        
        # Validate the (potentially fixed) CSV
        if not batch.validate_csv_file(fixed_content):
            raise HTTPException(
                status_code=400, 
                detail=f"File '{file.filename}' is not a valid CSV file or could not be automatically fixed"
            )
        
        # Use the fixed content if fixes were applied
        content = fixed_content
    
    # Generate unique filename
    timestamp = str(int(time.time() * 1000))
    file_path = os.path.join(upload_dir, f"{timestamp}_{file.filename}")
    
    # Save the file (using potentially fixed content)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
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

@app.post("/datasets/batch-upload", response_model=List[DatasetRead])
async def batch_upload_datasets(
    name_prefix: str = Form(...),
    description: Optional[str] = Form(None),
    format: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple dataset files at once"""
    return await batch.process_batch_upload(files, name_prefix, format, description, db)

@app.post("/datasets/upload-zip", response_model=List[DatasetRead])
async def upload_zip_dataset(
    name_prefix: str = Form(...),
    description: Optional[str] = Form(None),
    format: str = Form(...),
    zip_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a zip file containing multiple datasets"""
    if not zip_file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")
    
    return await batch.process_zip_upload(zip_file, name_prefix, format, description, db)

@app.put("/datasets/{dataset_id}", response_model=DatasetRead)
def update_dataset(
    dataset_id: int, 
    dataset_update: DatasetUpdate, 
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_active_user)
):
    """Update a dataset by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Update fields if provided
    if dataset_update.name is not None:
        dataset.name = dataset_update.name
    if dataset_update.description is not None:
        dataset.description = dataset_update.description
    if dataset_update.format is not None:
        dataset.format = dataset_update.format
    
    db.commit()
    db.refresh(dataset)
    return dataset

@app.delete("/datasets/{dataset_id}")
def delete_dataset(
    dataset_id: int, 
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_active_user)
):
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

# Metrics endpoints
@app.post("/datasets/{dataset_id}/metrics/", response_model=MetricsRead)
def create_metrics(
    dataset_id: int, 
    metrics: MetricsCreate, 
    db: Session = Depends(get_db)
):
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

@app.post("/datasets/{dataset_id}/metrics/batch", response_model=List[MetricsRead])
def batch_create_metrics(
    dataset_id: int,
    metrics_data: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_active_user)
):
    """Create multiple metrics entries for a dataset in one operation"""
    return batch.process_batch_metrics(metrics_data, dataset_id, db)

@app.get("/datasets/{dataset_id}/metrics/", response_model=List[MetricsRead])
def get_dataset_metrics(dataset_id: int, db: Session = Depends(get_db)):
    """Get all metrics for a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return db.query(DatasetMetrics).filter(DatasetMetrics.dataset_id == dataset_id).all()

@app.get("/metrics/search", response_model=List[MetricsRead])
def search_metrics(
    dataset_id: Optional[int] = None,
    model_name: Optional[str] = None,
    min_accuracy: Optional[float] = None,
    min_f1: Optional[float] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search metrics with filters"""
    return search.search_metrics(
        db=db,
        dataset_id=dataset_id,
        model_name=model_name,
        min_accuracy=min_accuracy,
        min_f1=min_f1,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset
    )

@app.get("/metrics/{metrics_id}", response_model=MetricsRead)
def get_metrics(metrics_id: int, db: Session = Depends(get_db)):
    """Get metrics by ID"""
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
    if metrics is None:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return metrics

@app.put("/metrics/{metrics_id}", response_model=MetricsRead)
def update_metrics(
    metrics_id: int, 
    metrics_update: MetricsUpdate, 
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_active_user)
):
    """Update metrics by ID"""
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    # Update fields if provided in a cleaner way
    update_data = metrics_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(metrics, key, value)
    
    db.commit()
    db.refresh(metrics)
    return metrics

@app.delete("/metrics/{metrics_id}")
def delete_metrics(
    metrics_id: int, 
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_active_user)
):
    """Delete metrics by ID"""
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    # Delete from database
    db.delete(metrics)
    db.commit()
    
    return {"status": "ok", "message": f"Metrics {metrics_id} deleted"}

# Export endpoints
@app.get("/datasets/{dataset_id}/export/json")
def export_dataset_json(dataset_id: int, db: Session = Depends(get_db)):
    """Export dataset to JSON"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.dataset_id == dataset_id).all()
    
    # Generate JSON content
    content = exporters.export_dataset_to_json(dataset, metrics)
    
    # Create download response
    response = StreamingResponse(iter([content]), media_type="application/json")
    response.headers["Content-Disposition"] = f"attachment; filename=dataset_{dataset_id}.json"
    return response

@app.get("/datasets/{dataset_id}/export/metrics/csv")
def export_metrics_csv(dataset_id: int, db: Session = Depends(get_db)):
    """Export metrics to CSV"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    metrics = db.query(DatasetMetrics).filter(DatasetMetrics.dataset_id == dataset_id).all()
    
    # Generate CSV content
    content = exporters.export_metrics_to_csv(metrics)
    
    # Create download response
    response = StreamingResponse(iter([content]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=metrics_{dataset_id}.csv"
    return response

# Visualization endpoints
@app.get("/visualizations/accuracy-comparison")
def get_accuracy_comparison(dataset_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get accuracy comparison data for visualization"""
    return visualization.get_accuracy_comparison(db, dataset_id)

@app.get("/visualizations/latency-data")
def get_latency_visualization(dataset_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get latency data for visualization"""
    return visualization.get_latency_data(db, dataset_id)

@app.get("/visualizations/distribution")
def get_distribution_visualization(dataset_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get distribution data for visualization"""
    return visualization.get_distribution_chart_data(db, dataset_id)

@app.get("/visualizations/models-over-time")
def get_models_over_time(db: Session = Depends(get_db)):
    """Get model performance over time"""
    return visualization.get_models_over_time(db)

# Summary endpoint
@app.get("/metrics/summary")
def get_metrics_summary(dataset_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get summary statistics for all metrics or filtered by dataset"""
    return search.get_metrics_summary(db, dataset_id)


