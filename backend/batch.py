"""
Batch processing functionality for AI Model Evaluation Platform.
Handles batch operations on datasets and metrics.
"""

import os
import json
import shutil
import zipfile
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from db.models import Dataset, DatasetMetrics


async def process_batch_upload(
    files: List[UploadFile],
    name_prefix: str,
    format: str,
    description: Optional[str],
    db: Session
) -> List[Dataset]:
    """
    Process a batch upload of multiple dataset files
    
    Args:
        files: List of uploaded files
        name_prefix: Prefix for dataset names
        format: Format of the datasets
        description: Optional description for datasets
        db: Database session
        
    Returns:
        List of created Dataset objects
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    created_datasets = []
    
    # Process each file
    for i, file in enumerate(files):
        # Generate unique filename with timestamp
        import time
        timestamp = str(int(time.time() * 1000) + i)
        file_path = os.path.join(upload_dir, f"{timestamp}_{file.filename}")
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create dataset in database
        dataset_name = f"{name_prefix}_{i+1}" if len(files) > 1 else name_prefix
        
        db_dataset = Dataset(
            name=dataset_name,
            description=description,
            format=format,
            file_path=file_path,
            size=os.path.getsize(file_path)
        )
        
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        created_datasets.append(db_dataset)
    
    return created_datasets


async def process_zip_upload(
    zip_file: UploadFile,
    name_prefix: str,
    format: str,
    description: Optional[str],
    db: Session
) -> List[Dataset]:
    """
    Process a zip file containing multiple dataset files
    
    Args:
        zip_file: Uploaded zip file
        name_prefix: Prefix for dataset names
        format: Format of the datasets
        description: Optional description for datasets
        db: Database session
        
    Returns:
        List of created Dataset objects
    """
    # Create upload directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save zip file temporarily
        tmp_zip_path = os.path.join(tmp_dir, zip_file.filename)
        with open(tmp_zip_path, "wb") as buffer:
            shutil.copyfileobj(zip_file.file, buffer)
        
        # Extract zip file
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        
        # Process extracted files
        created_datasets = []
        extracted_files = [f for f in os.listdir(tmp_dir) 
                          if os.path.isfile(os.path.join(tmp_dir, f)) and f != zip_file.filename]
        
        for i, filename in enumerate(extracted_files):
            # Generate unique filename with timestamp
            import time
            timestamp = str(int(time.time() * 1000) + i)
            source_path = os.path.join(tmp_dir, filename)
            dest_path = os.path.join(upload_dir, f"{timestamp}_{filename}")
            
            # Copy file to uploads directory
            shutil.copy2(source_path, dest_path)
            
            # Create dataset in database
            dataset_name = f"{name_prefix}_{i+1}" if len(extracted_files) > 1 else name_prefix
            
            db_dataset = Dataset(
                name=dataset_name,
                description=description,
                format=format,
                file_path=dest_path,
                size=os.path.getsize(dest_path)
            )
            
            db.add(db_dataset)
            db.commit()
            db.refresh(db_dataset)
            created_datasets.append(db_dataset)
    
    return created_datasets


def process_batch_metrics(
    metrics_data: List[Dict[str, Any]],
    dataset_id: int,
    db: Session
) -> List[DatasetMetrics]:
    """
    Process batch creation of metrics for a dataset
    
    Args:
        metrics_data: List of metrics data dictionaries
        dataset_id: ID of the dataset to associate metrics with
        db: Database session
        
    Returns:
        List of created DatasetMetrics objects
    """
    # Check if dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    
    created_metrics = []
    
    for metric_data in metrics_data:
        # Ensure dataset_id is set correctly
        metric_data["dataset_id"] = dataset_id
        
        # Create metrics in database
        db_metrics = DatasetMetrics(
            dataset_id=dataset_id,
            model_name=metric_data.get("model_name"),
            accuracy=metric_data.get("accuracy"),
            precision=metric_data.get("precision"),
            recall=metric_data.get("recall"),
            f1_score=metric_data.get("f1_score"),
            latency=metric_data.get("latency"),
            timestamps=metric_data.get("timestamps"),
            distribution=metric_data.get("distribution")
        )
        
        db.add(db_metrics)
        db.commit()
        db.refresh(db_metrics)
        created_metrics.append(db_metrics)
    
    return created_metrics 