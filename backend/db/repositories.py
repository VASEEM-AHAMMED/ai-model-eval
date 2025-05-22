import os
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import shutil

from db.models import Dataset, DatasetMetrics
from schemas import DatasetCreate, MetricsCreate

class DatasetRepository:
    @staticmethod
    def create_dataset(db: Session, dataset: DatasetCreate, file: UploadFile) -> Dataset:
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
            name=dataset.name,
            description=dataset.description,
            format=dataset.format,
            file_path=file_path,
            size=os.path.getsize(file_path)
        )
        
        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)
        
        return db_dataset
    
    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> Optional[Dataset]:
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    @staticmethod
    def get_datasets(db: Session, skip: int = 0, limit: int = 100) -> List[Dataset]:
        return db.query(Dataset).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_dataset(db: Session, dataset_id: int) -> bool:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return False
        
        # Delete the file
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        
        # Delete from database
        db.delete(dataset)
        db.commit()
        
        return True

class MetricsRepository:
    @staticmethod
    def create_metrics(db: Session, metrics: MetricsCreate) -> DatasetMetrics:
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
    
    @staticmethod
    def get_metrics(db: Session, metrics_id: int) -> Optional[DatasetMetrics]:
        return db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
    
    @staticmethod
    def get_metrics_by_dataset(db: Session, dataset_id: int) -> List[DatasetMetrics]:
        return db.query(DatasetMetrics).filter(DatasetMetrics.dataset_id == dataset_id).all()
    
    @staticmethod
    def delete_metrics(db: Session, metrics_id: int) -> bool:
        metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == metrics_id).first()
        if not metrics:
            return False
        
        # Delete from database
        db.delete(metrics)
        db.commit()
        
        return True 